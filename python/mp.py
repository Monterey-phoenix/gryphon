#!/usr/bin/env python3

from argparse import ArgumentParser
import os
from os.path import exists, isdir
from os import mkdir
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow

from gui_manager import GUIManager
from path_constants import RIGAL_ROOT, RIGAL_RC, RIGAL_SCRATCH, \
                           MP_CODE_DEFAULT_EXAMPLE, make_rigal_scratch
from mp_popup import mp_popup

# main
if __name__=="__main__":

    # create the "application" and the main window
    application = QApplication(sys.argv)
    main_window = QMainWindow()

    # create MP GUI manager
    gui_manager = GUIManager(main_window)

    if not exists(RIGAL_RC):
        # bad setup
        if exists(RIGAL_ROOT):
            error = "Trace Generator compiler is not available at %s." \
                    "  Is it built?  Aborting."% RIGAL_SC
        else:
            error = "Trace Generator is not available at %s." \
                    "  Is it installed?  Aborting."% RIGAL_ROOT
        mp_popup(None, error)
        print(error)

    else:
        # make sure RIGAL scratch exists
        make_rigal_scratch()

        # start default
        gui_manager.open_mp_code(MP_CODE_DEFAULT_EXAMPLE)

        # start the GUI
        sys.exit(application.exec_())

