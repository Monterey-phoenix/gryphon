from PyQt5.QtWidgets import qApp
from PyQt5.QtCore import QObject
from PyQt5.QtCore import QThread
from PyQt5.QtCore import pyqtSignal, pyqtSlot

# helper
# parse line number from MP Code compiler error message
def parse_error_line_number(line):
    if line[:14] == "*** error: at ":
        line_number = int(line.split()[3])
    else:
        # unexpected line
        line_number = 0
    return line_number

class MPCodeSyntaxChecker(QObject):
    # signals
    signal_syntax_report = pyqtSignal(int, str) # line number or 0, error or ""

    def __init__(self, mp_code_editor, trace_generator_manager):
        super(MPCodeSyntaxChecker, self).__init__()

        self.mp_code_editor = mp_code_editor
        self.trace_generator_manager = trace_generator_manager

        # run syntax check when document contents change
        self.mp_code_editor.code_editor.document().contentsChanged.connect(
                                                    self.run_syntax_check)

        self.old_mp_code_text = ""

    @pyqtSlot()
    def run_syntax_check(self):
        # text
        mp_code_text = self.mp_code_editor.text()

        # contentsChanged is triggered when formatting changes,
        # so only service change when text changes.
        if mp_code_text == self.old_mp_code_text:
            # done, do not signal syntax report
            return

        self.old_mp_code_text = mp_code_text

        # schema name and mp_code text
        schema_name = self.mp_code_editor.schema_name()

        # perform check
        status = self.trace_generator_manager.mp_check_syntax(
                                                 schema_name, mp_code_text)

        # signal result of syntax check
        line_number = parse_error_line_number(status)
        self.signal_syntax_report.emit(line_number, status)

