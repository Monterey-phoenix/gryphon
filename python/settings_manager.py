
#
# Modification History:
#   180803 David Shifflett
#     Switched default (nps_theme) code quoted text color
#     from yellow (hard to see) to orange
#

"""Settings are kept in the settings directory.  Access them using this manager.

Provides the following services:
  Global variables, do not directly change their values.
     settings - the active settings
     nps_theme_settings
     firebird_theme_settings
     printer_friendly_settings - good on printer
     bright_settings - good on screen
  Note: settings is global and also signal_settings_changed provides settings.

  Class SettingsManager, provides methods to safely change and notify settings:
     copy() - get your copy of settings
     change(provided settings) - change provided settings values, signal change
     _load(), load_from() - change all settings values from file, signal change
     _save(), save_to(fname), save settings to user default file or named file

Usage:
  Use SettingsManager to initialize or modify the global settings variable.
  SettingsManager is a singleton because it manages the settings resource.
  Instantiate SettingsManager before relying on settings values.
  Listen to the signal_settings_changed signal if you need to respond to change.
  Access the settings global variable without needing SettingsManager.
"""
from os.path import expanduser
import os
import json
from PyQt5.QtCore import QObject # for signal/slot support
from PyQt5.QtCore import pyqtSignal, pyqtSlot # for signal/slot support
from PyQt5.QtCore import Qt
from mp_popup import mp_popup
from path_constants import MP_SETTINGS_FILENAME

# user's default path
def _settings_filename():
    home = expanduser("~")
    settings_filename = os.path.join(home, MP_SETTINGS_FILENAME)
    return settings_filename

# NPS theme
nps_theme_settings = json.loads('{"node_width": 127, "node_height": 10, "node_t_contrast": 171, "node_border": false, "node_shadow": false, "node_root_c": "#00486f", "node_atomic_c": "#1f7dbc", "node_composite_c": "#ffcc00", "node_schema_c": "#70017f", "node_say_c": "#ffffa0", "edge_arrow_size": 10, "edge_in_c": "#dbdbdb", "edge_follows_c": "#000000", "edge_user_defined_c": "#7aa7bc", "edge_in_style": "dash_line", "edge_follows_style": "solid_line", "edge_user_defined_style": "solid_line", "graph_background_c": "#ffffff", "graph_gradient": 111, "graph_h_spacing": 165, "graph_v_spacing": 55, "graph_hide_collapse_opacity": 127, "mp_code_comment_c":"#606060", "mp_code_keyword_c":"#760f7f","mp_code_meta_symbol_c":"#760f7f","mp_code_operator_c":"#000000","mp_code_number_c":"#000000","mp_code_variable_c":"#404040", "mp_code_quoted_text_c":"#ffaa00"}')

# Firebird theme
firebird_theme_settings = json.loads('{"node_width": 127, "node_height": 10, "node_t_contrast": 210, "node_border": false, "node_shadow": false, "node_root_c": "#027731", "node_atomic_c": "#1f7dbc", "node_composite_c": "#ff6a00", "node_schema_c": "#866ec4", "node_say_c": "#ffffa0", "edge_arrow_size": 10, "edge_in_c": "#7d7d82", "edge_follows_c": "#000000", "edge_user_defined_c": "#0000ff", "edge_in_style": "dash_line", "edge_follows_style": "solid_line", "edge_user_defined_style": "solid_line", "graph_background_c": "#ffffff", "graph_gradient": 100, "graph_h_spacing": 165, "graph_v_spacing": 55}')

# printer-friendly
printer_friendly_settings = json.loads('{"node_width": 127, "node_height": 10, "node_border": true, "node_shadow": true, "node_root_c": "#aaff7f", "node_atomic_c": "#c5e9ff", "node_composite_c": "#ffaa7f", "node_schema_c": "#008000", "node_say_c": "#ffff66", "edge_arrow_size": 10, "edge_in_c": "#808080", "edge_follows_c": "#000000", "edge_user_defined_c": "#0000ff", "edge_in_style": "dash_line", "edge_follows_style": "solid_line", "edge_user_defined_style": "solid_line", "graph_background_c": "#e8e8e8", "graph_gradient": 130, "graph_h_spacing": 165, "graph_v_spacing": 55, "node_t_contrast": 96}')

# high contrast
high_contrast_settings = json.loads('{"node_width": 127, "node_height": 10, "node_border": true, "node_shadow": true, "node_root_c": "#00d600", "node_atomic_c": "#92beff", "node_composite_c": "#ff9966", "node_schema_c": "#008000", "node_say_c": "#ffff66", "edge_arrow_size": 10, "edge_in_c": "#808080", "edge_follows_c": "#000000", "edge_user_defined_c": "#0000ff", "edge_in_style": "dash_line", "edge_follows_style": "solid_line", "edge_user_defined_style": "solid_line", "graph_background_c": "#c0c0c0", "graph_gradient": 120, "graph_h_spacing": 165, "graph_v_spacing": 55, "node_t_contrast": 100}')

# black and white
black_and_white_settings = json.loads('{"node_width": 127, "node_height": 10, "node_t_contrast": 0, "node_border": true, "node_shadow": false, "node_root_c": "#000000", "node_atomic_c": "#dddddd", "node_composite_c": "#dbdbdb", "node_schema_c": "#000000", "node_say_c": "#f1f1f1", "edge_arrow_size": 10, "edge_in_c": "#dbdbdb", "edge_follows_c": "#000000", "edge_user_defined_c": "#a0a0a0", "edge_in_style": "dash_line", "edge_follows_style": "solid_line", "edge_user_defined_style": "solid_line", "graph_background_c": "#ffffff", "graph_gradient": 100, "graph_h_spacing": 165, "graph_v_spacing": 55}')

# Grayscale
grayscale_settings = json.loads('{"node_width": 127, "node_height": 10, "node_t_contrast": 176, "node_border": false, "node_shadow": false, "node_root_c": "#555555", "node_atomic_c": "#e8e8e8", "node_composite_c": "#a2a2a2", "node_schema_c": "#000000", "node_say_c": "#e0e0e0", "edge_arrow_size": 10, "edge_in_c": "#dbdbdb", "edge_follows_c": "#000000", "edge_user_defined_c": "#a0a0a0", "edge_in_style": "dash_line", "edge_follows_style": "solid_line", "edge_user_defined_style": "solid_line", "graph_background_c": "#ffffff", "graph_gradient": 111, "graph_h_spacing": 165, "graph_v_spacing": 55}')

# SERC
serc_theme_settings = json.loads('{"node_width": 127, "node_height": 10, "node_t_contrast": 171, "node_border": false, "node_shadow": false, "node_root_c": "#aa1039", "node_atomic_c": "#e1e3e8", "node_composite_c": "#969696", "node_schema_c": "#550000", "node_say_c": "#e0dfc2", "edge_arrow_size": 10, "edge_in_c": "#dbdbdb", "edge_follows_c": "#000000", "edge_user_defined_c": "#a07c7c", "edge_in_style": "dash_line", "edge_follows_style": "solid_line", "edge_user_defined_style": "solid_line", "graph_background_c": "#ffffff", "graph_gradient": 111, "graph_h_spacing": 165, "graph_v_spacing": 55}')

# Navy
navy_theme_settings = json.loads('{"node_width": 127, "node_height": 10, "node_t_contrast": 185, "node_border": false, "node_shadow": false, "node_root_c": "#7b0000", "node_atomic_c": "#333a6a", "node_composite_c": "#bca15d", "node_schema_c": "#550000", "node_say_c": "#e6e1ab", "edge_arrow_size": 10, "edge_in_c": "#dbdbdb", "edge_follows_c": "#000000", "edge_user_defined_c": "#5d627f", "edge_in_style": "dash_line", "edge_follows_style": "solid_line", "edge_user_defined_style": "solid_line", "graph_background_c": "#ffffff", "graph_gradient": 119, "graph_h_spacing": 165, "graph_v_spacing": 55}')

settings_themes = [
    ("NPS theme", nps_theme_settings),
    ("Firebird theme", firebird_theme_settings),
    ("Black-and-white", black_and_white_settings),
    ("Grayscale", grayscale_settings),
    ("SERC theme", serc_theme_settings),
    ("Navy theme", navy_theme_settings),
    ("Printer-friendly", printer_friendly_settings),
    ("High contrast", high_contrast_settings)
]

settings = dict()

# SettingsManager provides services to manage the global settings variable
# and to signal change.  Do not modify settings directly.
class SettingsManager(QObject):

    # signal
    signal_settings_changed = pyqtSignal(dict, dict, name='settingsChanged')

    def __init__(self):
        super(SettingsManager, self).__init__()

        # load default settings
        if os.path.exists(_settings_filename()):
            self._load()
        else:
            self.change(nps_theme_settings)

    # get a copy of settings
    def copy(self):
        copy = dict()
        for key, value in settings.items():
            copy[key] = value
        return copy

    # change provided settings
    @pyqtSlot()
    def change(self, new_settings):
        global settings
        old_settings = settings.copy()
        for key, value in new_settings.items():
            settings[key] = value

        # signal change
        self.signal_settings_changed.emit(old_settings, settings)

        # save settings in user store
        self._save()

    def save_to(self, filename):

        # export settings in JSON
        try:
            with open(filename, "w") as f:
                json.dump(settings, f)
        except Exception as e:
            mp_popup(None, "Error saving settings file: %s" % str(e))

    def _save(self):
        self.save_to(_settings_filename())
        
    def load_from(self, filename):
        try:
            with open(filename) as f:
                new_settings = json.load(f)

            # add any missing settings
            missing_keys = nps_theme_settings.keys() - new_settings.keys()
            for key in missing_keys:
                new_settings[key] = nps_theme_settings[key]

            self.change(new_settings)

        except Exception as e:
            mp_popup(None, "Error reading settings file: %s" % str(e))

    def _load(self):
        self.load_from(_settings_filename())

