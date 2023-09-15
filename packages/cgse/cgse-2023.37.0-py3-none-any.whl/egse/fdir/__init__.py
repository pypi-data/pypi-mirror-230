from egse.control import Response
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox, QApplication, QDialog, QLabel, QVBoxLayout
from PyQt5.QtGui import QFont

def generate_popup(code: str, actions: str, success: bool) -> Response:
    app = QApplication([])
    msg = QMessageBox()
    msg.setModal(False)
    msg.setWindowModality(0)
    msg.setWindowTitle("FDIR signal notification")
    msg.setIcon(QMessageBox.Critical)
    msg.setText(f"<h1><bold>An FDIR signal with code:<br><blockquote>{code}</blockquote><br> has fired!</bold></h1>")
    if success:
        msg.setInformativeText(f"The associated recovery script was executed: <br><h2> succesfully! </h2><br> \n\nPlease press OK to clear FDIR signal")
    else:
        msg.setInformativeText(f"The associated recovery script has: <br> <h2>FAILED!</h2> <br> Please take action to recover the system\n\nAfter recovery press OK to clear FDIR signal")
    
    msg.setDetailedText(f"Required actions:\n\n {actions}")
    msg.setStandardButtons(QMessageBox.Ok)
    msg.setDefaultButton(QMessageBox.Ok)
    
    ret = msg.exec_()
    
    if ret == QMessageBox.Ok:
        pass
    else:
        pass