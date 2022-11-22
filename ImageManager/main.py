import os
import sys

from pathlib import Path

from PyQt6.QtWidgets import QMainWindow, QApplication
from PyQt6 import uic, QtWidgets
from ImageManager.gui.windows import main_window
from ImageManager import app as wlh_app

from ImageManager.gui import globals as gui_globals


# class MainWindow(QMainWindow):
# def __init__(self):
#     super(MainWindow, self).__init__()
#     mod_db.check_first_run()
#     mod_gui.init(self)

def main():
    app = QApplication(sys.argv)

    path = Path(os.getcwd(), 'gui', 'windows', 'main_window', 'window.ui')
    gui_globals.main_window = uic.loadUi(str(path))

    wlh_app.check_first_run()
    main_window.setup()

    gui_globals.main_window.show()

    app.exec()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
