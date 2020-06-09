import os
from subprocess import Popen, PIPE
#import shutil
import json
import queue
from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtCore import QTimer
from command_runner import CommandRunner
from path_constants import RIGAL_SCRATCH, RIGAL_RC, RIGAL_IC

"""Run MP Code trace generator engines.

Interfaces:
    mp_compile(schema_name, scope, mp_code_text):
        return (status, generated_json, log)
        note that status is "" on no error and may start with "*** error: at "
    mp_cancel_compile()
    mp_check_syntax()
    mp_clean_shutdown()

NOTE: RIGAL functions read/write in same directory, so we change to the
scratch RIGAL work directory to work, then move back when done.
"""

# the syntax checker runs RIGAL commands in the GUI thread
def _run_rigal_now(cmd):
    p = Popen(cmd, stdout=PIPE)
    lines = p.communicate()[0].decode('utf-8').split("\n")
    if p.returncode != 0:
        print("error with command", cmd)
        print("lines", lines)
        print("Aborting.")
        raise Exception("_run_rigal command aborted.")

    return lines

class TraceGeneratorManager(QObject):

    # signals
    # register with this to receive completed compile response
    #                                    status, generated_json, log
    signal_compile_response = pyqtSignal(str, str, str)

    # states
    # IDLE, S1, S2, S3, S4, S5, S6

    # start timer and follow states to compile or cancel
    def __init__(self):
        super(TraceGeneratorManager, self).__init__()
        self.should_cancel = False
        self.state = "IDLE"
        self._log = list()
        self._queue = queue.Queue()
        self._timer = QTimer(self)
        self._timer.setSingleShot(False)
        self._timer.timeout.connect(self._handle_state)
        self._timer.start(100) # 100ms
        self.command_runner = None

        # Remember user's directory.
        # We must temporarily work in the rigal_scratch directory,
        # which acts thread-globally and is invasive.
        # We must do this because RIGAL tools require it.
        # The RIGAL design should be modified to prevent the requirement
        # for relative-path opertions while compiling.
        self._cwd = os.getcwd()

    def _add_log(self, name, do_add):
        while not self._queue.empty():
            stream_name, line = self._queue.get()
            line = line.rstrip()
            if stream_name == "stderr":
                if do_add:
                    self._log.append("Error: %s" % line)
                print("Error: %s: %s" % (name, line))
             
            else:
                if do_add:
                    self._log.append(line)
                print("%s: %s" % (name, line))

    def _log_string(self):
        return "\n".join(self._log)

    def _return_to_idle(self):
        if self.state == "IDLE":
            return

        # remove any generated schema-related scratch files
        for f in ["xd", "RIGCOMP.TMP",
                  "%s"%self.schema_name,
                  "%s.cpp"%self.schema_name,
                  "%s.json"%self.schema_name,
                  "%s.mp"%self.schema_name]:
            try:
                os.remove(f)
            except Exception:
                pass

        # return to the working directory the user started in
        os.chdir(self._cwd)

        # clear state
        self.state = "IDLE"
        self._log.clear()
        self.should_cancel = False
        self.command_runner = None
        self.schema_name = ""

    def _manage_bad_return_code(self):
        if self.command_runner.return_code():
            # signal error
            self.signal_compile_response.emit("Return code error", "{}",
                                                     self._log_string())
            self._return_to_idle()
            return True
        else:
            return False

    # read generated JSON file.  Return (status, generated_json)
    def _read_generated_json_file(self):

        # parse the generated JSON filename
        generated_json_filename = "%s.json"%self.schema_name

        try:
            # get json data
            with open(generated_json_filename) as f:
                generated_json_text = f.read()
            return ("", generated_json_text)

        except Exception as e:
            status = "Error reading generated file '%s': %s" % (
                                      generated_json_filename, str(e))
            return (status, "")

    # initiate stateful compilation process
    """Call this to get compilation started"""
    def mp_compile(self, schema_name, scope, mp_code_text):

        # validate state
        if self.state != "IDLE":
            self.signal_compile_response.emit("Unexpected state: %s" %
                                                    self.state, "{}", "")
            return

        # bad if RIGAL is not built
        if not os.path.isfile(RIGAL_RC):
            # emit: status, JSON, log
            self.signal_compile_response.emit("Error: no %s"%RIGAL_RC, "{}", "")
            return

        # the schema name
        self.schema_name = schema_name

        # set commands
        # 1: rc MP2-parser
        self.command_1 = [RIGAL_RC, "MP2-parser"]
        # 2: ic MP2-parser
        self.command_2 = [RIGAL_IC, "MP2-parser", schema_name,
                                                  "tree", "%d"%scope]
        # 3: rc MP2-generator
        self.command_3 = [RIGAL_RC, "MP2-generator"]
        # 4: ic MP2-generator tree
        self.command_4 = [RIGAL_IC, "MP2-generator", "tree"]
        # 5: ic MP2-generator tree
        self.command_5 = ["g++", "%s.cpp"%schema_name, "-o", schema_name, "-O3"]
        # 6: run schema_name
        self.command_6 = ["./%s"%schema_name]

        # temporarily work in the rigal_scratch directory
        # NOTE: this acts thread-globally and is invasive.
        # We must do this because RIGAL tools require it.
        # The design should prevent relative-path opertions while compiling.
        self._cwd = os.getcwd()
        os.chdir(RIGAL_SCRATCH)

        # write MP Code text to file for RIGAL tools
        try:
            with open("%s.mp" % schema_name, 'w') as f:
                f.write(mp_code_text)
        except Exception as e:
            status = "Error writing temporary %s.mp file: %s" % (schema_name,
                                                                 str(e))
            self.signal_compile_response.emit(status, "{}", "")
            self._return_to_idle()
            return

        # transition to state S1
        self._log.clear()
        self.command_runner = CommandRunner(self.command_1, self._queue)
        self.state = "S1"

    # timer repeatedly calls this
    @pyqtSlot()
    def _handle_state(self):
        if self.state == "IDLE":
            return
        #print("State: %s" % self.state)

        # active states are busy until command runner is done
        if not self.command_runner.is_done():
            return

        # when here we are in an active state and command runner is done

        if self.state == "S1":
            self._add_log("lines1", False)
            if self._manage_bad_return_code():
                return

            # transition to state S2
            self.command_runner = CommandRunner(self.command_2, self._queue)
            self.state = "S2"
            return

        if self.state == "S2":
            # abort on error
            # https://stackoverflow.com/questions/8196254/how-to-iterate-queue-queue-items-in-python/8196904
            # note queue.queue is not threadsafe but this is not in a thread
            # so this is okay
            for stream_name, line in list(self._queue.queue):
                if line[:14] == "*** error: at ":
                    # error
                    self.signal_compile_response.emit(line, "{}", "")
                    self._return_to_idle()
                    return

            self._add_log("lines2", True)
            if self._manage_bad_return_code():
                return

            # transition to state S3
            self.command_runner = CommandRunner(self.command_3, self._queue)
            self.state = "S3"
            return

        if self.state == "S3":
            self._add_log("lines3", False)
            if self._manage_bad_return_code():
                return

            # transition to state S4
            self.command_runner = CommandRunner(self.command_4, self._queue)
            self.state = "S4"
            return

        if self.state == "S4":
            self._add_log("lines4", False)
            if self._manage_bad_return_code():
                return

            # transition to state S5
            self.command_runner = CommandRunner(self.command_5, self._queue)
            self.state = "S5"
            return

        if self.state == "S5":
            self._add_log("lines5", False)
            if self._manage_bad_return_code():
                return

            # transition to state S6
            self.command_runner = CommandRunner(self.command_6, self._queue)
            self.state = "S6"
            return

        if self.state == "S6":
            self._add_log("lines6", True)
            if self._manage_bad_return_code():
                return

            # done
            # get generated JSON
            status, generated_json = self._read_generated_json_file()
            if status:
                self.signal_compile_response.emit(status, "{}",
                                                  self._log_string())
                self._return_to_idle()
                return

            # everything worked
            self.signal_compile_response.emit("", generated_json,
                                                  self._log_string())
            self._return_to_idle()
            return

    """Call this to abort the compilation process."""
    def mp_cancel_compile(self):
        # validate state
        if (self.state == "IDLE"):
            self.signal_compile_response.emit("Unexpected state: %s"%self.state)
            return

        if self.command_runner:
            self.command_runner.kill()
        self.command_runner = None
        self._return_to_idle()
        self.signal_compile_response.emit("Canceled", "{}", "")

    """Check MP Code syntax synchronously.  Returns "" else error which
    may include the line number of ther error"""
    def mp_check_syntax(self, schema_name, mp_code_text):

        try:

            # temporarily work in the rigal_scratch directory
            # NOTE: this acts thread-globally and is invasive.
            # We must do this because RIGAL tools require it.
            # The design should prevent relative-path opertions while compiling.
            os.chdir(RIGAL_SCRATCH)

            # write MP Code text to file for RIGAL tools
            try:
                with open("%s.mp" % schema_name, 'w') as f:
                    f.write(mp_code_text)
            except Exception as e:
                return "Error writing temporary %s.mp file: %s" % (schema_name,
                                                                   str(e))

            # rc MP2-parser
            lines_1 = _run_rigal_now([RIGAL_RC, "MP2-parser"])

            # rc schema
            lines_2 = _run_rigal_now([RIGAL_IC, "MP2-parser", schema_name,
                                      "tree", "1"])

            # maybe return error
            error_lines = list()
            track_errors = False
            for l in lines_2:
                if l[:14] == "*** error: at ":
                    track_errors = True
                if l[:18] == "Errors detected...":
                    track_errors = False
                if track_errors:
                    error_lines.append(l.strip())

            # done, return any error on one line
            return " ".join(error_lines)

        finally:
            # always restore the working directory path
            os.chdir(self._cwd)

    # clean shutdown
    @pyqtSlot()
    def mp_clean_shutdown(self):
        # kill command runner if active
        if self.command_runner:
            self.command_runner.kill()

