# wrapper from https://stackoverflow.com/questions/2398800/linking-a-qtdesigner-ui-file-to-python-pyqt
import os
from PyQt5.QtCore import QObject # for signal/slot support
from PyQt5.QtCore import pyqtSlot # for signal/slot support
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QFileDialog
from settings_dialog import Ui_SettingsDialog
from color_selector_widget import ColorSelectorWidget
from settings_manager import settings

# user's preferred Settings path
preferred_settings_dir = os.path.expanduser("~")

# a suggested settings filename
def _suggested_settings_filename():
    return os.path.join(preferred_settings_dir, "mp_gryphon_gui_settings.stg")

class SettingsDialogWrapper(QDialog):
    def __init__(self, parent, settings_manager):
        super(SettingsDialogWrapper, self).__init__(parent)
        self.parent = parent
        self.settings_manager = settings_manager
        self.ui = Ui_SettingsDialog()
        self.ui.setupUi(self)

        # old setings
        self.old_settings = settings_manager.copy()
        self.ui.node_width_slider.setValue(self.old_settings["node_width"])
        self.ui.node_height_slider.setValue(self.old_settings["node_height"])
        self.ui.node_t_contrast_slider.setValue(
                                 self.old_settings["node_t_contrast"])
        self.ui.node_border_cb.setChecked(self.old_settings["node_border"])
        self.ui.node_shadow_cb.setChecked(self.old_settings["node_shadow"])
        self.ui.graph_gradient_slider.setValue(
                                 self.old_settings["graph_gradient"])
        self.ui.graph_h_spacing_slider.setValue(
                                 self.old_settings["graph_h_spacing"])
        self.ui.graph_v_spacing_slider.setValue(
                                 self.old_settings["graph_v_spacing"])
        self.ui.graph_hide_collapse_slider.setValue(
                          self.old_settings["graph_hide_collapse_opacity"])

        self.ui.edge_arrow_size_slider.setValue(
                                 self.old_settings["edge_arrow_size"])
        self.set_button_colors()

        # load/save
        self.ui.load_pb.clicked.connect(self.load_pb_clicked)
        self.ui.save_pb.clicked.connect(self.save_pb_clicked)

        # Nodes
        self.ui.button_box.accepted.connect(self.accept)
        self.ui.button_box.rejected.connect(self.cancel)
        self.ui.node_width_slider.sliderMoved.connect(
                                 self.node_width_slider_moved)
        self.ui.node_height_slider.sliderMoved.connect(
                                 self.node_height_slider_moved)
        self.ui.node_t_contrast_slider.sliderMoved.connect(
                                 self.node_t_contrast_slider_moved)
        self.ui.node_border_cb.toggled.connect(self.node_border_toggled)
        self.ui.node_shadow_cb.toggled.connect(self.node_shadow_toggled)

        self.ui.node_root_c_pb.clicked.connect(self.node_root_c_pb_clicked)
        self.ui.node_atomic_c_pb.clicked.connect(
                                 self.node_atomic_c_pb_clicked)
        self.ui.node_composite_c_pb.clicked.connect(
                                 self.node_composite_c_pb_clicked)
        self.ui.node_schema_c_pb.clicked.connect(
                                 self.node_schema_c_pb_clicked)
        self.ui.node_say_c_pb.clicked.connect(self.node_say_c_pb_clicked)

        # Graph
        self.ui.graph_background_c_pb.clicked.connect(
                                 self.graph_background_c_pb_clicked)
        self.ui.graph_gradient_slider.sliderMoved.connect(
                                 self.graph_gradient_slider_moved)
        self.ui.graph_h_spacing_slider.sliderMoved.connect(
                                 self.graph_h_spacing_slider_moved)
        self.ui.graph_v_spacing_slider.sliderMoved.connect(
                                 self.graph_v_spacing_slider_moved)
        self.ui.graph_hide_collapse_slider.sliderMoved.connect(
                                 self.graph_hide_collapse_slider_moved)

        # Edges
        self.ui.edge_arrow_size_slider.sliderMoved.connect(
                                 self.edge_arrow_size_slider_moved)
        self.ui.edge_in_c_pb.clicked.connect(self.edge_in_c_pb_clicked)
        self.ui.edge_follows_c_pb.clicked.connect(
                                 self.edge_follows_c_pb_clicked)
        self.ui.edge_user_defined_c_pb.clicked.connect(
                                 self.edge_user_defined_c_pb_clicked)

        # MP Code
        self.ui.mp_code_comment_c_pb.clicked.connect(
                                 self.mp_code_comment_c_pb_clicked)
        self.ui.mp_code_keyword_c_pb.clicked.connect(
                                 self.mp_code_keyword_c_pb_clicked)
        self.ui.mp_code_variable_c_pb.clicked.connect(
                                 self.mp_code_variable_c_pb_clicked)
        self.ui.mp_code_number_c_pb.clicked.connect(
                                 self.mp_code_number_c_pb_clicked)
        self.ui.mp_code_operator_c_pb.clicked.connect(
                                 self.mp_code_operator_c_pb_clicked)
        self.ui.mp_code_quoted_text_c_pb.clicked.connect(
                                 self.mp_code_quoted_text_c_pb_clicked)
        self.ui.mp_code_meta_symbol_c_pb.clicked.connect(
                                 self.mp_code_meta_symbol_c_pb_clicked)


    # set button colors to match present settings
    def set_button_colors(self):
        # nodes
        self.ui.node_root_c_pb.setStyleSheet(
                  "background-color: %s" % settings["node_root_c"])
        self.ui.node_atomic_c_pb.setStyleSheet(
                  "background-color: %s" % settings["node_atomic_c"])
        self.ui.node_composite_c_pb.setStyleSheet(
                  "background-color: %s" % settings["node_composite_c"])
        self.ui.node_schema_c_pb.setStyleSheet(
                  "background-color: %s" % settings["node_schema_c"])
        self.ui.node_say_c_pb.setStyleSheet(
                  "background-color: %s" % settings["node_say_c"])

        # graph
        self.ui.graph_background_c_pb.setStyleSheet(
                  "background-color: %s" % settings["graph_background_c"])

        # edges
        self.ui.edge_in_c_pb.setStyleSheet(
                  "background-color: %s" % settings["edge_in_c"])
        self.ui.edge_follows_c_pb.setStyleSheet(
                  "background-color: %s" % settings["edge_follows_c"])
        self.ui.edge_user_defined_c_pb.setStyleSheet(
                  "background-color: %s" % settings["edge_user_defined_c"])

        # mp code
        self.ui.mp_code_comment_c_pb.setStyleSheet(
                  "background-color: %s" % settings["mp_code_comment_c"])
        self.ui.mp_code_keyword_c_pb.setStyleSheet(
                  "background-color: %s" % settings["mp_code_keyword_c"])
        self.ui.mp_code_variable_c_pb.setStyleSheet(
                  "background-color: %s" % settings["mp_code_variable_c"])
        self.ui.mp_code_number_c_pb.setStyleSheet(
                  "background-color: %s" % settings["mp_code_number_c"])
        self.ui.mp_code_operator_c_pb.setStyleSheet(
                  "background-color: %s" % settings["mp_code_operator_c"])
        self.ui.mp_code_quoted_text_c_pb.setStyleSheet(
                  "background-color: %s" % settings["mp_code_quoted_text_c"])
        self.ui.mp_code_meta_symbol_c_pb.setStyleSheet(
                  "background-color: %s" % settings["mp_code_meta_symbol_c"])

    def closeEvent(self, e):
        # abort by restoring settngs when user deliberately closes the window
        self.settings_manager.change(self.old_settings)

    @pyqtSlot()
    def cancel(self):
        # restore
        self.settings_manager.change(self.old_settings)

    # load settings
    @pyqtSlot()
    def load_pb_clicked(self):
        global preferred_settings_dir
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog

        settings_filename, _ = QFileDialog.getOpenFileName(self.parent,
                        "Load MP Gryphon GUI settings file",
                        _suggested_settings_filename(),
                        "MP Gryphon GUI Settings files (*.stg);;All Files (*)",
                        options=options)

        if settings_filename:

            # remember the preferred path
            head, _tail = os.path.split(settings_filename)
            preferred_settings_dir = head

            # load settings from file
            self.settings_manager.load_from(settings_filename)

    # save settings
    @pyqtSlot()
    def save_pb_clicked(self):
        global preferred_settings_dir
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog

        settings_filename, _ = QFileDialog.getSaveFileName(self.parent,
                        "Save MP Gryphon GUI settings file",
                        _suggested_settings_filename(),
                        "MP Gryphon GUI Settings files (*.stg);;All Files (*)",
                        options=options)

        if settings_filename:

            # remember the preferred path
            head, _tail = os.path.split(settings_filename)
            preferred_settings_dir = head

            # save settings to file
            self.settings_manager.save_to(settings_filename)

    # nodes
    @pyqtSlot(int)
    def node_width_slider_moved(self, value):
        self.settings_manager.change({"node_width":value})

    @pyqtSlot(int)
    def node_height_slider_moved(self, value):
        self.settings_manager.change({"node_height":value})

    @pyqtSlot(int)
    def node_t_contrast_slider_moved(self, value):
        self.settings_manager.change({"node_t_contrast":value})

    @pyqtSlot(int)
    def edge_arrow_size_slider_moved(self, value):
        self.settings_manager.change({"edge_arrow_size":value})

    @pyqtSlot(bool)
    def node_border_toggled(self, state):
        self.settings_manager.change({"node_border":state})

    @pyqtSlot(bool)
    def node_shadow_toggled(self, state):
        self.settings_manager.change({"node_shadow":state})

    @pyqtSlot()
    def node_root_c_pb_clicked(self):
        ColorSelectorWidget(self, self.settings_manager, "node_root_c")
        self.set_button_colors()

    @pyqtSlot()
    def node_atomic_c_pb_clicked(self):
        ColorSelectorWidget(self, self.settings_manager, "node_atomic_c")
        self.set_button_colors()

    @pyqtSlot()
    def node_composite_c_pb_clicked(self):
        ColorSelectorWidget(self, self.settings_manager, "node_composite_c")
        self.set_button_colors()

    @pyqtSlot()
    def node_schema_c_pb_clicked(self):
        ColorSelectorWidget(self, self.settings_manager, "node_schema_c")
        self.set_button_colors()

    @pyqtSlot()
    def node_say_c_pb_clicked(self):
        ColorSelectorWidget(self, self.settings_manager, "node_say_c")
        self.set_button_colors()

    # graph
    @pyqtSlot()
    def graph_background_c_pb_clicked(self):
        ColorSelectorWidget(self, self.settings_manager, "graph_background_c")
        self.set_button_colors()

    @pyqtSlot(int)
    def graph_gradient_slider_moved(self, value):
        self.settings_manager.change({"graph_gradient":value})

    @pyqtSlot(int)
    def graph_h_spacing_slider_moved(self, value):
        self.settings_manager.change({"graph_h_spacing":value})

    @pyqtSlot(int)
    def graph_v_spacing_slider_moved(self, value):
        self.settings_manager.change({"graph_v_spacing":value})

    @pyqtSlot(int)
    def graph_hide_collapse_slider_moved(self, value):
        self.settings_manager.change({"graph_hide_collapse_opacity":value})

    # edges
    @pyqtSlot()
    def edge_in_c_pb_clicked(self):
        ColorSelectorWidget(self, self.settings_manager, "edge_in_c")
        self.set_button_colors()

    @pyqtSlot()
    def edge_follows_c_pb_clicked(self):
        ColorSelectorWidget(self, self.settings_manager, "edge_follows_c")
        self.set_button_colors()

    @pyqtSlot()
    def edge_user_defined_c_pb_clicked(self):
        ColorSelectorWidget(self, self.settings_manager, "edge_user_defined_c")
        self.set_button_colors()

    # mp code
    @pyqtSlot()
    def mp_code_comment_c_pb_clicked(self):
        ColorSelectorWidget(self, self.settings_manager, "mp_code_comment_c")
        self.set_button_colors()

    @pyqtSlot()
    def mp_code_keyword_c_pb_clicked(self):
        ColorSelectorWidget(self, self.settings_manager, "mp_code_keyword_c")
        self.set_button_colors()

    @pyqtSlot()
    def mp_code_variable_c_pb_clicked(self):
        ColorSelectorWidget(self, self.settings_manager, "mp_code_variable_c")
        self.set_button_colors()

    @pyqtSlot()
    def mp_code_number_c_pb_clicked(self):
        ColorSelectorWidget(self, self.settings_manager, "mp_code_number_c")
        self.set_button_colors()

    @pyqtSlot()
    def mp_code_operator_c_pb_clicked(self):
        ColorSelectorWidget(self, self.settings_manager, "mp_code_operator_c")
        self.set_button_colors()

    @pyqtSlot()
    def mp_code_quoted_text_c_pb_clicked(self):
        ColorSelectorWidget(self, self.settings_manager, "mp_code_quoted_text_c")
        self.set_button_colors()

    @pyqtSlot()
    def mp_code_meta_symbol_c_pb_clicked(self):
        ColorSelectorWidget(self, self.settings_manager, "mp_code_meta_symbol_c")
        self.set_button_colors()

