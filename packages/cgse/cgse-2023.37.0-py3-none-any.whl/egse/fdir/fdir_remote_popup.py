import logging
import sys
from argparse import ArgumentParser

from egse.control import Response
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox, QApplication, QDialog, QLabel, QVBoxLayout
from PyQt5.QtGui import QFont

from egse.fdir import generate_popup

# This function can be used generates a pop-up window when an FDIR situation was triggered.
# This is put into a separate module to avoid having to run the QT thread in the control server
# (where the popup is generated). There are probably better ways to do this but this works.
def main():

    logger = logging.getLogger(__name__)

    parser = ArgumentParser()
    parser.add_argument('code', type=str, help='FDIR code string')
    parser.add_argument('success', type=str, help='recovery script success')
    parser.add_argument('actions', type=str, help='actions taken')
    args = parser.parse_args()
    
    generate_popup(args.code, args.success, args.actions)
    


if __name__ == '__main__':
    main()
    sys.exit()