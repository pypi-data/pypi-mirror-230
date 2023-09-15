import os
import sys
import logging
import psutil
import subprocess
import threading
import time

from PyQt5.QtWidgets import QMessageBox, QApplication

from egse.control import Response, Success, Failure
from egse.fdir.fdir_remote_interface import FdirRemoteInterface
# from egse.fdir.fdir_manager import FdirManagerProxy

logger = logging.getLogger(__name__)


class FdirRemoteController(FdirRemoteInterface):
    def __init__(self):
        self.dialog = None

    def is_connected(self):
        return True
    
    def is_simulator(self):
        return False
    
    def kill_process(self, pid: int) -> Response:

        try:
            process = psutil.Process(pid)
        except psutil.NoSuchProcess:
            logger.warning(f"Could not find a process with PID {pid}.")
            return Failure(f"Could not find a process with PID {pid}.")
        else:
            process.kill()
            logger.info(f"Killed registered script with PID {pid}.")
            return Success("")

    def generate_popup(self, code: str, actions: str, success: bool) -> Response:

        path = os.path.dirname(os.path.abspath(__file__))
        subprocess.Popen(['python3', f'{path}/fdir_remote_popup.py', code, actions, str(success)])

        


if __name__ == "__main__":
    fdir = FdirRemoteController()
    fdir.generate_popup("FDIR_CS_STOPPED", "rip", True)