import logging

import sys
from PyQt5.QtWidgets import QMessageBox, QApplication

LOGGER = logging.getLogger(__name__)


def parse_arguments(args):

    process_name_index = args.index("--process_name")
    message_index = args.index("--message")

    if process_name_index < message_index:
        process_name = " ".join(args[process_name_index + 1: message_index])
        message = " ".join(args[message_index + 1:])
    else:
        message = " ".join(args[message_index + 1: process_name_index])
        process_name = " ".join(args[process_name_index + 1:])

    return process_name, message


def main():

    app = QApplication([])

    process_name, message = parse_arguments(sys.argv)

    error_message = QMessageBox()
    error_message.setIcon(QMessageBox.Warning)
    error_message.setWindowTitle("Error")
    error_message.setText(f"The {process_name} could not be started!")
    error_message.setInformativeText(f"{message}\n\nCheck the log for more information. \n\nIt could also be useful to "
                                     f"start the {process_name} on the command line (on the EGSE server) to see "
                                     f"whether you get more information.")
    error_message.setStandardButtons(QMessageBox.Ok)

    return error_message.exec()


if __name__ == "__main__":
    main()
