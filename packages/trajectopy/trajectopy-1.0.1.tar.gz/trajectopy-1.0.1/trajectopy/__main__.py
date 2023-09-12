"""
Trajectopy - Trajectory Evaluation in Python

Gereon Tombrink, 2023
mail@gtombrink.de
"""
import ctypes
import os
import logging
from PyQt6.QtWidgets import QApplication
from PyQt6 import QtGui
from trajectopy.gui.main_window import TrajectopyGUI, VERSION
from trajectopy.util.path import ICON_FILE_PATH


if os.name == "nt":
    myappid = f"gereont.trajectopy.main.{VERSION}"
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

logging.basicConfig(
    format="%(levelname)-8s %(asctime)s.%(msecs)03d - %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)


def main():
    app = QApplication([])
    _ = TrajectopyGUI()
    app.setWindowIcon(QtGui.QIcon(ICON_FILE_PATH))
    app.exec()


if __name__ == "__main__":
    main()
