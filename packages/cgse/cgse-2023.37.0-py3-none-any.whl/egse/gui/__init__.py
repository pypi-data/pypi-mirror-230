from PyQt5.QtWidgets import QFrame
from PyQt5.QtWidgets import QMessageBox


def show_warning_message(description: str, info_text: str = None, detailed_text: str = None):
    msg_box = QMessageBox()

    msg_box.setWindowTitle("Warning")
    msg_box.setIcon(QMessageBox.Warning)
    msg_box.setText(description)
    if info_text is not None:
        msg_box.setInformativeText(info_text)
    if detailed_text is not None:
        msg_box.setDetailedText(detailed_text)
    msg_box.setStandardButtons(QMessageBox.Ok)
    msg_box.exec_()


def show_info_message(description: str, info_text: str = None, detailed_text: str = None):
    msg_box = QMessageBox()

    msg_box.setWindowTitle("Warning")
    msg_box.setIcon(QMessageBox.Information)
    msg_box.setText(description)
    if info_text is not None:
        msg_box.setInformativeText(info_text)
    if detailed_text is not None:
        msg_box.setDetailedText(detailed_text)
    msg_box.setStandardButtons(QMessageBox.Ok)
    msg_box.exec_()


class VLine(QFrame):
    """Presents a simple Vertical Bar that can be used in e.g. the status bar."""

    def __init__(self):
        super().__init__()
        self.setFrameShape(self.VLine | self.Sunken)


class QHLine(QFrame):
    """Presents a simple Horizontal Bar that can be used in e.g. the status bar."""

    def __init__(self):
        super(QHLine, self). __init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)
