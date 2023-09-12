"""
Trajectopy - Trajectory Evaluation in Python

Gereon Tombrink, 2023
mail@gtombrink.de
"""
from functools import wraps
import uuid
from PyQt6 import QtWidgets


def show_progress(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # emit signal to show progress bar
        args[0].operation_started.emit()

        # execute the function
        func(*args, **kwargs)

        # emit signal to hide progress bar
        args[0].operation_finished.emit()

    return wrapper


def show_msg_box(message: str):
    message_box = QtWidgets.QMessageBox()
    message_box.setText(message)
    message_box.exec()


def read_file_dialog(
    parent,
    file_filter: str = "All (*.*)",
    mode: QtWidgets.QFileDialog.FileMode = QtWidgets.QFileDialog.FileMode.ExistingFiles,
):
    file_dialog = QtWidgets.QFileDialog(parent=parent)
    file_dialog.setFileMode(mode)
    fileName, _ = file_dialog.getOpenFileNames(caption="Open File", directory="", filter=file_filter)
    return fileName


def save_file_dialog(parent, file_filter: str = "All (*.*)"):
    file_dialog = QtWidgets.QFileDialog()
    file_dialog.setFileMode(QtWidgets.QFileDialog.FileMode.AnyFile)
    fileName, _ = file_dialog.getSaveFileName(parent, caption="Select Output File", directory="", filter=file_filter)
    return fileName


def browse_dir_dialog(parent) -> str:
    file_dialog = QtWidgets.QFileDialog()
    file_dialog.setFileMode(QtWidgets.QFileDialog.FileMode.Directory)
    return file_dialog.getExistingDirectory(parent, caption="Select Directory", directory="")


def bool_to_str(input: bool) -> str:
    return "yes" if input else "no"


def generate_id() -> str:
    return str(uuid.uuid4())
