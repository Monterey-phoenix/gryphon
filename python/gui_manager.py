
#
# Modification History:
#   180803 David Shifflett
#     Added graph_list_column and trace_navigation classes
#

from PyQt5.QtWidgets import QMainWindow, QAction
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtWidgets import QStyle # for PM_ScrollBarExtent
from PyQt5.QtWidgets import QActionGroup
from PyQt5.QtWidgets import qApp
from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QUrl
from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSlot
import os
import webbrowser
from version_file import VERSION
from main_splitter import MainSplitter
from mp_code_column import MPCodeColumn
from graph_list_column import GraphListColumn
from trace_navigation import TraceNavigation
from graph_main_widget import GraphMainWidget
from graph_list_widget import GraphListWidget
from graph_list_width_manager import GraphListWidthManager
from scope_spinner import ScopeSpinner
from graph_status_label import GraphStatusLabel
from graphs_manager import GraphsManager
from mp_code_editor import MPCodeEditor
from logger import Logger
import mp_code_io_manager
from mp_code_syntax_checker import parse_error_line_number
from trace_generator_manager import TraceGeneratorManager
import export_trace_manager
from settings_manager import SettingsManager, settings_themes
from settings_dialog_wrapper import SettingsDialogWrapper
from keyboard_dialog_wrapper import KeyboardDialogWrapper
from about_mp_dialog_wrapper import AboutMPDialogWrapper
from event_menu import EventMenu
from mp_code_syntax_checker import MPCodeSyntaxChecker
from path_constants import MP_CODE_EXAMPLES

"""MP main window containing menu, toolbar, statusbar, and central widget.
Central widget contains split pane areas, ref. http://firebird.nps.edu/:
  code_area
  console_area
  graph_area
  graph_list_area
"""

class GUIManager(QObject):

    def __init__(self, main_window):
        super(GUIManager, self).__init__()

        # user's preferred MP Code path
        self.preferred_mp_code_dir = os.path.expanduser("~")

        # user's preferred JSON Graph Gryphon file path
        self.preferred_gry_file_dir = os.path.expanduser("~")

        # user's preferred JPG trace path
        self.preferred_trace_dir = os.path.expanduser("~")

        # the settings manager
        self.settings_manager = SettingsManager()

        # the graphs manager
        self.graphs_manager = GraphsManager(self.settings_manager)

        # the graph list width manager
        self.graph_list_width_manager = GraphListWidthManager(
                  main_window.style().pixelMetric(QStyle.PM_ScrollBarExtent))

        # state
        self.w = main_window

        # main window decoration
        self.w.setGeometry(0,0,850,800)
        self.w.setWindowTitle("Monterey Phoenix v4 - Gryphon GUI %s"%VERSION)
        self.w.setWindowIcon(QIcon('icons/MP-logo-small-blue.png'))

        # the main splitter which emits size_changed
        main_splitter = MainSplitter(self.graph_list_width_manager)

        # the scope spinner containing spinner=QSpinBox
        self.scope_spinner = ScopeSpinner()

        # the graph list widget which responds to events
        self.graph_list_widget = GraphListWidget(main_splitter,
                                                 self.graphs_manager,
                                                 self.graph_list_width_manager)

        # the graph main widget
        self.graph_main_widget = GraphMainWidget(self.graphs_manager,
                                                 self.graph_list_widget)
        # the graph list widget repaints when a node coordinate in the
        # main widget changes
        self.graph_main_widget.signal_graph_item_view_changed.connect(
                           self.graph_list_widget.graph_item_view_changed)

        # the event menu
        self.event_menu = EventMenu(self.graphs_manager,
                                    self.graph_list_widget,
                                    self.settings_manager)

        # the graph status widget
        self.graph_status_label = GraphStatusLabel(self.graphs_manager)

        # the statusbar
        self.statusbar = self.w.statusBar()
        self.statusbar.addPermanentWidget(self.graph_status_label.status_text)
        self.statusbar.showMessage("Open, Import, or Compose MP Code to begin.")

        # the logger containing log_pane=QPlainTextEdit
        self.logger = Logger(self.statusbar)

        # the trace generator manager which runs the compiler asynchronously
        self.trace_generator_manager = TraceGeneratorManager()
        self.trace_generator_manager.signal_compile_response.connect(
                                        self.response_compile_mp_code)

        # the MP Code editor
        self.mp_code_editor = MPCodeEditor(self.settings_manager,
                                                         self.statusbar)

        # the syntax checker
        self.mp_code_syntax_checker = MPCodeSyntaxChecker(self.mp_code_editor,
                                        self.trace_generator_manager)
        self.mp_code_syntax_checker.signal_syntax_report.connect(
                                        self.mp_code_editor.set_syntax_status)

        # setup
        self.define_actions()
        self.define_menus()
        self.define_toolbar()

        # trace navigation widget
        self.trace_navigation = TraceNavigation(self.graphs_manager,
                                        self.graph_list_widget)
        self.trace_navigation.setDisabled(True)

        # the central widget containing the main split pane
        self.mp_code_column = MPCodeColumn(self)
        self.mp_code_column.set_sizes([600,200])
        self.graph_list_column = GraphListColumn(self)
        self.graph_list_column.set_sizes([50,600])
        main_splitter.addWidget(self.mp_code_column)
        main_splitter.addWidget(self.graph_main_widget.view)
        main_splitter.addWidget(self.graph_list_column)
        main_splitter.setSizes([250,500,100])
        self.w.setCentralWidget(main_splitter)

        # clean shutdown
        qApp.aboutToQuit.connect(self.trace_generator_manager.mp_clean_shutdown)

        self.w.show()

    # actions
    def define_actions(self):
        # action exit
        self.action_exit = QAction(QIcon("icons/application-exit.png"),
                                   "&Exit", self.w)
        self.action_exit.setShortcut('Ctrl+Q')
        self.action_exit.setStatusTip("Exit MP")
        self.action_exit.triggered.connect(self.w.close)

        # action help
        self.action_help = QAction(QIcon("icons/help-contents-5.png"),
                                   "&Help", self.w)
        self.action_help.setShortcut('Ctrl+H')
        self.action_help.setStatusTip("Help using MP")
        self.action_help.triggered.connect(self.help_mp)

        # action keyboard_shortcuts
        self.action_keyboard_shortcuts = QAction("&Keyboard Shortcuts", self.w)
        self.action_keyboard_shortcuts.setStatusTip(
                                        "Keyboard shorcuts for MP controls")
        self.action_keyboard_shortcuts.triggered.connect(
                                        self.keyboard_shortcuts)

        # action about
        self.action_about = QAction(QIcon("icons/document-properties.png"),
                                        "&About MP", self)
        self.action_about.setStatusTip("about MP")
        self.action_about.triggered.connect(self.about_mp)

        # action run
        self.action_run = QAction(QIcon("icons/run-build-install.png"),
                                        "&Run", self)
        self.action_run.setShortcut('Ctrl+R')
        self.action_run.setStatusTip("Generate traces from MP Code")
        self.action_run.triggered.connect(self.request_compile_mp_code)

        # action cancel
        self.action_cancel = QAction(QIcon("icons/dialog-cancel-3.png"),
                                        "&Stop", self)
        self.action_cancel.setStatusTip("Cancel trace generation process")
        self.action_cancel.triggered.connect(self.cancel_compile_mp_code)
        self.action_cancel.setDisabled(True)

        # action clear log
        self.action_clear_log = QAction(QIcon("icons/edit-clear-list.png"),
                                        "&Clear MP Code Log", self)
        self.action_clear_log.setShortcut('Ctrl+L')
        self.action_clear_log.setStatusTip("Clear MP Code log")
        self.action_clear_log.triggered.connect(self.logger.clear_log)

        # action open MP Code file
        self.action_open_mp_code_file = QAction(QIcon(
                       "icons/document-open-2.png"), "&Open...", self)
        self.action_open_mp_code_file.setStatusTip("Open MP Code File")
        self.action_open_mp_code_file.triggered.connect(
                                           self.select_and_open_mp_code_file)

        # action close MP Code file
        self.action_close_mp_code_file = QAction(QIcon(
                       "icons/document-close.png"), "Close", self)
        self.action_close_mp_code_file.setStatusTip("Close MP Code File")
        self.action_close_mp_code_file.triggered.connect(self.close_mp_code)

        # action save MP Code file
        self.action_save_mp_code_file = QAction(QIcon(
                       "icons/document-save-2.png"), "&Save...", self)
        self.action_save_mp_code_file.setStatusTip("Save MP Code file")
        self.action_save_mp_code_file.triggered.connect(
                                           self.save_mp_code_file)

        # action import JSON Graph Format .gry file
        self.action_import_gry_file = QAction(QIcon(
                   "icons/document-import-2.png"), "&Import...", self)
        self.action_import_gry_file.setStatusTip("Import Gryphon Graph file")
        self.action_import_gry_file.triggered.connect(
                                     self.select_and_import_gry_file)

        # action export JSON Graph Format .gry file
        self.action_export_gry_file = QAction(QIcon(
                   "icons/document-export-4.png"), "&Export...", self)
        self.action_export_gry_file.setStatusTip("Export Gryphon Graph file")
        self.action_export_gry_file.triggered.connect(
                                     self.select_and_export_gry_file)

        # action export trace as image file
        self.action_export_trace = QAction("&Export Trace...", self)
        self.action_export_trace.setStatusTip("Export trace as image file")
        self.action_export_trace.triggered.connect(
                                     self.select_and_export_trace)

        # action export all traces as image files
        self.action_export_all_traces = QAction("&Export All Traces...", self)
        self.action_export_all_traces.setStatusTip(
                                           "Export all traces as image files")
        self.action_export_all_traces.triggered.connect(
                                     self.select_and_export_all_traces)

        # action settings custom...
        self.action_settings_custom = QAction("&Custom...", self)
        self.action_settings_custom.setStatusTip(
                                     "Draw using custom settings")
        self.action_settings_custom.triggered.connect(
                                     self.set_settings_custom)

        # events action button which opens the event menu
        self.action_event_menu_button = QAction(QIcon("icons/Events_icon.png"),
                                              "Events", self)
        self.action_event_menu_button.setStatusTip("Manage event groups")
        self.action_event_menu_button.setMenu(self.event_menu.event_menu)

    # menus
    def define_menus(self):
        menubar = self.w.menuBar()
        menubar.setNativeMenuBar(False)

        # menu | file
        file_menu = menubar.addMenu('&File')

        # menu | file | open
        file_menu.addAction(self.action_open_mp_code_file)

        # menu | file | close
        file_menu.addAction(self.action_close_mp_code_file)

        # menu | file | open examples
        self.open_examples_menu = file_menu.addMenu("Open Example")
        self.open_examples_menu.setStatusTip("Open MP Code Example")
        for filename in sorted(os.listdir(MP_CODE_EXAMPLES)):
            if filename.endswith(".mp"):
                # add action with dedicated lambda function containing filename
                action = QAction(filename, self)
                action.triggered.connect(lambda checked, filename=
                            os.path.join(MP_CODE_EXAMPLES, filename):
                                    self.open_mp_code(filename))
                self.open_examples_menu.addAction(action)
      
        # menu | file | save MP Code
        file_menu.addAction(self.action_save_mp_code_file)

        # menu | file | separator
        file_menu.addSeparator()

        # menu | file | import Gryphon Graph file
        file_menu.addAction(self.action_import_gry_file)

        # menu | file | export Gryphon Graph file
        file_menu.addAction(self.action_export_gry_file)

        # menu | file | separator
        file_menu.addSeparator()

        # menu | file | export trace
        file_menu.addAction(self.action_export_trace)

        # menu | file | export all traces
        file_menu.addAction(self.action_export_all_traces)

        # menu | file | separator
        file_menu.addSeparator()

        # menu | file | exit
        file_menu.addAction(self.action_exit)

        # menu | actions
        actions_menu = menubar.addMenu('&Actions')

        # menu | actions | run
        actions_menu.addAction(self.action_run)

        # menu | actions | cancel
        actions_menu.addAction(self.action_cancel)

        # menu | actions | separator
        file_menu.addSeparator()

        # menu | actions | clear log
        actions_menu.addAction(self.action_clear_log)

        # menu | preferences
        preferences_menu = menubar.addMenu('&Preferences')

        # menu | preferences | settings
        settings_menu = preferences_menu.addMenu("Settings")

        # menu | preferences | settings options
        for theme_name, theme in settings_themes:

            # add action with dedicated lambda function containing filename
            action = QAction(theme_name, self)
            action.triggered.connect(lambda checked, theme=theme:
                                     self.settings_manager.change(theme))
            settings_menu.addAction(action)

        settings_menu.addSeparator()
        settings_menu.addAction(self.action_settings_custom)

#        # menu | preferences | separator
#        preferences_menu.addSeparator()

        # menu | help
        help_menu = menubar.addMenu('&Help')
        help_menu.addAction(self.action_help)
        help_menu.addAction(self.action_keyboard_shortcuts)
        help_menu.addAction(self.action_about)

    # toolbar items
    def define_toolbar(self):
        toolbar = self.w.addToolBar("MP_Py Toolbar")
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        toolbar.addAction(self.action_open_mp_code_file)
        toolbar.addWidget(self.scope_spinner.spinner)
        toolbar.addWidget(QLabel("Scope"))
        toolbar.addAction(self.action_run)
        toolbar.addAction(self.action_cancel)
        toolbar.addAction(self.action_event_menu_button)

    ############################################################
    # action handlers
    ############################################################

    # help...
    @pyqtSlot()
    def help_mp(self):
        path = os.path.abspath("../doc/mp_py_um/mp_py_um.pdf")
        if not os.path.exists(path):
            path = os.path.abspath("pdf/mp_py_um.pdf")
        if os.path.exists(path):
            webbrowser.open("file://%s"%path)
        else:
            self.logger.log("Error: Missing help file.")

    # Keyboard Shortcuts...
    @pyqtSlot()
    def keyboard_shortcuts(self):
        wrapper = KeyboardDialogWrapper(self.w)
        wrapper.show()

    # About MP...
    @pyqtSlot()
    def about_mp(self):
        wrapper = AboutMPDialogWrapper(self.w)
        wrapper.show()

    # Open MP Code file
    @pyqtSlot()
    def select_and_open_mp_code_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filename, _ = QFileDialog.getOpenFileName(self.w,
        "Open MP Code file",
        self.preferred_mp_code_dir,
        "MP Code files (*.mp);;All Files (*)", options=options)

        if filename:
            # remember the preferred path
            head, tail = os.path.split(filename)
            self.preferred_mp_code_dir = head

            # open the file
            self.open_mp_code(filename)

    # Save MP Code file
    @pyqtSlot()
    def save_mp_code_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog

        # suggested filename
        schema_name = self.mp_code_editor.schema_name()
        if not schema_name:
            schema_name = "unnamed"
        suggested_filename = "%s.mp" % schema_name

        mp_code_filename, _ = QFileDialog.getSaveFileName(self.w,
        "Save MP Code file",
        os.path.join(self.preferred_mp_code_dir, suggested_filename),
        "MP Code files (*.mp);;All Files (*)", options=options)

        if mp_code_filename:
            # remember the preferred path
            head, _tail = os.path.split(mp_code_filename)
            self.preferred_mp_code_dir = head

            # save the file
            status = mp_code_io_manager.save_mp_code_file(
                              self.mp_code_editor.text(), mp_code_filename)
            if status:
                # log failure
                self.logger.log(status)
            else:
                # great, exported.
                self.logger.log("Saved to file %s" % mp_code_filename)

    # import Gryphon Graph file
    @pyqtSlot()
    def select_and_import_gry_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filename, _ = QFileDialog.getOpenFileName(self.w,
        "Import Gryphon Graph file",
        self.preferred_gry_file_dir,
        "Gryphon graph files (*.gry);;All Files (*)", options=options)

        if filename:
            # remember the preferred path
            head, _tail = os.path.split(filename)
            self.preferred_gry_file_dir = head

            # import the file
            self.import_gry_file(filename)

    # export Gryphon Graph file
    @pyqtSlot()
    def select_and_export_gry_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog

        # suggested filename
        schema_name = self.mp_code_editor.schema_name()
        if not schema_name:
            schema_name = "unnamed"
        suggested_filename = "%s_scope_%d.gry" % (schema_name,
                                              self.scope_spinner.scope())

        filename, _ = QFileDialog.getSaveFileName(self.w,
        "Export Gryphon Graph file",
        os.path.join(self.preferred_gry_file_dir, suggested_filename),
        "Gryphon graph files (*.gry);;All Files (*)", options=options)

        if filename:
            # remember the preferred path
            head, _tail = os.path.split(filename)
            self.preferred_gry_file_dir = head

            # export the file
            self.export_gry_file(filename)

    # export trace as image file
    @pyqtSlot()
    def select_and_export_trace(self):

        graph = self.graph_list_widget.selected_graph()
        if not graph:
            self.logger.log("Error exporting trace: There are no traces")
            return

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog

        # suggested filename
        schema_name = self.mp_code_editor.schema_name()
        if not schema_name:
            schema_name = "unnamed"
        suggested_filename = "%s_%03d.png" % (schema_name, graph.index)

        filename, _ = QFileDialog.getSaveFileName(self.w,
        "Export trace image file",
        os.path.join(self.preferred_trace_dir, suggested_filename),
        "MP trace image files (*.png);;All Files (*)", options=options)

        if filename:
            # remember the preferred path
            head, _tail = os.path.split(filename)
            self.preferred_trace_dir = head

            # export the trace as image file
            self.export_trace(filename)

    # export traces as image files under path
    @pyqtSlot()
    def select_and_export_all_traces(self):

        graph = self.graph_list_widget.selected_graph()
        if not len(self.graphs_manager.graphs):
            self.logger.log("Error exporting trace: There are no traces")
            return

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog

        # suggested filename
        schema_name = self.mp_code_editor.schema_name()
        if not schema_name:
            schema_name = "unnamed"

        filename_prefix, _ = QFileDialog.getSaveFileName(self.w,
          "Export serialized <File name>_nnn.png trace image files",
          os.path.join(self.preferred_trace_dir, schema_name),
          "MP trace image files (*.png);;All Files (*)", options=options)

        if filename_prefix:
            # remember the preferred path
            head, _tail = os.path.split(filename_prefix)
            self.preferred_trace_dir = head

            # export the file
            # export the traces as serialized image files
            self.export_serialized_traces(filename_prefix)

    @pyqtSlot()
    def set_settings_custom(self):
        wrapper = SettingsDialogWrapper(self.w, self.settings_manager)
        wrapper.exec_()

    ############################################################
    # primary interfaces
    ############################################################
    # open MP Code file
    def open_mp_code(self, mp_code_filename):
        status, mp_code_text = mp_code_io_manager.read_mp_code_file(
                                                         mp_code_filename)

        if status:
            # log failure
            self.logger.log(status)
        else:
            # accept request
            self.logger.clear_log()
            self.logger.log("Opened MP Code file %s" % mp_code_filename)
            self.mp_code_editor.set_text(mp_code_text)
            self.graphs_manager.clear_graphs()
            self.trace_navigation.clear()
            self.graph_main_widget.reset_view_orientation()

            # set visual state
            self.set_is_compiling(False)

            # no trace nav until after Run
            self.trace_navigation.setDisabled(True)

    # Close MP Code file
    @pyqtSlot()
    def close_mp_code(self):

        # accept request
        self.logger.clear_log()
        self.mp_code_editor.set_text("")
        self.graphs_manager.clear_graphs()
        self.trace_navigation.clear()
        self.graph_main_widget.reset_view_orientation()

        # no trace nav until after Open and Run
        self.trace_navigation.setDisabled(True)

    # compile MP Code
    @pyqtSlot()
    def request_compile_mp_code(self):
        # compile
        scope = self.scope_spinner.scope()
        schema_name = self.mp_code_editor.schema_name()
        mp_code_text = self.mp_code_editor.text()

        # set visual state
        self.set_is_compiling(True)

        self.logger.log("Compiling %s..." % schema_name)
        self.trace_generator_manager.mp_compile(
                                         schema_name, scope, mp_code_text)

    # receive response from trace generator manager request to compile MP Code
    @pyqtSlot(str, str, str)
    def response_compile_mp_code(self, status, generated_json_text, log):

        # log the compilation log
        self.logger.log(log)

        if status:
            # log failure
            self.logger.log(status)

            # set line number
            line_number = parse_error_line_number(status)
            self.mp_code_editor.set_error_line_number(line_number)

        else:
            # accept request
            status, graphs = mp_code_io_manager.read_generated_json(
                                                       generated_json_text)

            if status:
                # log failure
                self.logger.log(status)

                # clear graphs
                self.graphs_manager.clear_graphs()
                self.trace_navigation.clear()

                # no trace nav until after Open and Run
                self.trace_navigation.setDisabled(True)

            else:
                # accept graphs
                scope = self.scope_spinner.scope()
                schema_name = self.mp_code_editor.schema_name()
                self.graphs_manager.set_graphs(schema_name, scope, graphs)
                self.logger.log("Compiled %s" % schema_name)

                # select graph at first row
                # ref. https://stackoverflow.com/questions/6925951/how-to-select-a-row-in-a-qlistview
                if len(graphs) > 0:
                    self.graph_list_widget.select_graph(graphs[0])

        # set visual state
        self.set_is_compiling(False)

    # cancel compile MP Code
    @pyqtSlot()
    def cancel_compile_mp_code(self):
        # cancel
        schema_name = self.mp_code_editor.schema_name()
        self.logger.log("Canceling compiling %s" % schema_name)
        self.trace_generator_manager.mp_cancel_compile()

    # import Gryphon graph file
    def import_gry_file(self, gry_file_filename):
        self.logger.log("Importing Gryphon Graph file %s..." %
                                                          gry_file_filename)
        status, mp_code_text, scope, selected_index, \
                scale, x_slider, y_slider, graphs = \
                mp_code_io_manager.import_gry_file(gry_file_filename)

        if status:
            # log failure
            self.logger.log(status)

        else:
            # accept import request
            self.logger.clear_log()

            # set view to match JSON graph specifications
            self.mp_code_editor.set_text(mp_code_text)
            schema_name = self.mp_code_editor.schema_name()
            self.graphs_manager.set_graphs(schema_name, scope, graphs)
            self.graph_list_widget.select_graph(self.graphs_manager.find_graph(
                                                             selected_index))
            self.graph_main_widget.set_view_orientation(scale,
                                                       x_slider, y_slider)
            self.logger.log("Imported Gryphon Graph file %s" %
                                                       gry_file_filename)

            # set visual state
            self.set_is_compiling(False)

            # enable trace nav
            self.trace_navigation.setDisabled(False)

    # export Gryphon Graph file
    def export_gry_file(self, gry_file_filename):
        scale, x_slider, y_slider = \
                            self.graph_main_widget.get_view_orientation()
        if self.graph_list_widget.selected_graph():
            index = self.graph_list_widget.selected_graph().index
        else:
            index = 0
        status = mp_code_io_manager.export_gry_file(
                    gry_file_filename,
                    self.mp_code_editor.text(),
                    self.scope_spinner.scope(),
                    index,
                    scale, x_slider, y_slider,
                    self.graphs_manager.graphs)

        if status:
            # log failure
            self.logger.log(status)

        else:
            # great, exported.
            self.logger.log("Exported Gryphon Graph file %s" %
                                                        gry_file_filename)

    # export trace as image file
    def export_trace(self, trace_filename):
        status = export_trace_manager.export_trace(
                    trace_filename,
                    self.graph_list_widget.selected_graph())

        if status:
            # log failure
            self.logger.log(status)

        else:
            # great, exported.
            self.logger.log("Exported trace image file %s" % trace_filename)

    # export all traces as image files
    def export_serialized_traces(self, trace_filename_prefix):
        for graph in self.graphs_manager.graphs:
            trace_filename = "%s_%03d.png" % (trace_filename_prefix,
                                              graph.index)

            status = export_trace_manager.export_trace(
                        trace_filename, graph)

            if status:
                # log failure
                self.logger.log("%s.  Aborting." % status)
                break

            else:
                # great, exported.
                self.logger.log("Exported trace image file %s" % trace_filename)

    # run and cancel button state
    def set_is_compiling(self, is_compiling):

        # run and cancel
        self.action_run.setDisabled(is_compiling)
        self.action_cancel.setDisabled(not is_compiling)

        # trace navigation widgets
        self.trace_navigation.setDisabled(is_compiling)

        # other actions and menus
        self.action_open_mp_code_file.setDisabled(is_compiling)
        self.action_close_mp_code_file.setDisabled(is_compiling)
        self.open_examples_menu.setDisabled(is_compiling)
        self.action_import_gry_file.setDisabled(is_compiling)
        self.action_export_gry_file.setDisabled(is_compiling)
        self.action_export_trace.setDisabled(is_compiling)
        self.action_export_all_traces.setDisabled(is_compiling)

        # note: these two are disabled when compiling because the
        # local trace generator changes the local directory, which
        # makes these fail.
        self.action_help.setDisabled(is_compiling)
        self.action_about.setDisabled(is_compiling)

        # disable the code editor so it does not fire a contentsChanged event
        # which would trigger the syntax checker, which is not assynchronous.
        self.mp_code_editor.code_editor.setDisabled(is_compiling)

    # send a line of text to the log pane
    def write_log(self, log_line):
        self.logger.log(log_line)

