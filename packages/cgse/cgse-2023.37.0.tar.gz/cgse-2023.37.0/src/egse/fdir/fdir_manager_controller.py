import os
import re
import logging
import psutil
import subprocess

from threading import Thread
from datetime import datetime

import yaml

from PyQt5.QtWidgets import QMessageBox, QApplication, QDialog, QLabel, QVBoxLayout

from egse.setup import load_setup
from egse.settings import Settings
from egse.setup import get_setup
from egse.system import replace_environment_variable
from egse.control import Success
from egse.fdir.fdir_remote_interface import FdirRemoteInterface
from egse.fdir.fdir_remote import FdirRemoteProxy
from egse.fdir import generate_popup

logger = logging.getLogger(__name__)

CTRL_SETTINGS = Settings.load("FDIR Manager Control Server")
REMOTE_SETTINGS = Settings.load("FDIR Remote Control Server")


class FdirException(Exception):
    pass


class FdirManagerController(FdirRemoteInterface):

    def __init__(self):

        self._state = ""
        self._priority = -1
        self._local_pids = []
        self._remote_pids = []
        self._storage_path = replace_environment_variable(CTRL_SETTINGS.RECOVERY_SCRIPT_LOCATION)
        self._logging_path = replace_environment_variable(CTRL_SETTINGS.LOGGING_LOCATION)
        self._remote_proxy = FdirRemoteProxy()
        # Check if the remote is online.
        if not self._remote_proxy.is_cs_connected():
            logger.warning("FDIR Manager could not connect to the FDIR remote CS")
            # raise RuntimeError("FDIR Manager could not connect the the FDIR Remote CS")
        else:
            logger.info(f"connected to remote CS @ {REMOTE_SETTINGS.HOSTNAME}")

        # Try to load fdir table.
        try:
            self._fdir_table = load_setup().setup.gse.fdir_manager.configuration.table
        except AttributeError as ex:
            raise FdirException("Could not FDIR table from current setup") from ex


    def is_connected(self):
        return True
    
    def is_simulator(self):
        return False

    def register_script(self, host: str, pid: int):

        if self._state != 0:
            logger.error(f"Attempt to register script while state is not idle ({self._state}).")
            raise FdirException(
                f"Cannot register script because FDIR state is not idle ({self._state}).")

        elif host in ['localhost', os.uname()[1]]:

            if pid in self._local_pids:
                logger.error(f"Attempt to register existing PID {pid} @ localhost.")
                raise FdirException("PID is already registered.")
            else:
                self._local_pids.append(pid)
                logger.info(f"Successful registration of PID {pid} @ localhost.")

        elif host == REMOTE_SETTINGS.HOSTNAME:

            if pid in self._remote_pids:
                logger.error(f"Attempt to register existing PID {pid} @ {host}.")
                raise FdirException("PID is already registered.")
            else:
                self._remote_pids.append(pid)
                logger.info(f"Successful registration of PID {pid} @ {host}.")

        else:
            logger.error(f"Attempt to register a script with unknown hostname ({host})")
            raise FdirException("unknown hostname")


    def deregister_script(self, host: str, pid: int):

        if host in ['localhost', os.uname()[1]]:

            if pid not in self._local_pids[host]:
                logger.error(f"Attempt to deregister unknown PID {pid} @ localhost.")
                raise FdirException("PID is unknown.")
            else:
                self._pids[host].remove(pid)
                logger.info(f"Successful deregistration of PID {pid} @ localhost.")

        if host == REMOTE_SETTINGS.HOSTNAME:

            if pid not in self._local_pids[host]:
                logger.error(f"Attempt to deregister unknown PID {pid} @ {host}.")
                raise FdirException("PID is unknown.")
            else:
                self._pids[host].remove(pid)
                logger.info(f"Successful deregistration of PID {pid} @ {host}.")

        else:
            logger.error(f"attempt to deregister a script with unknown hostname ({host})")
            raise FdirException("unknown hostname")


    def signal_fdir(self, fdir_code: str, script_args: list):

        logger.info(f"Received FDIR code {fdir_code}: {script_args}.")

        # try to get the mitigation script name and priority from the fdir table
        try:
            recovery_command = self._fdir_table[fdir_code]['script']
            priority = self._fdir_table[fdir_code]['priority']
            actions = self._fdir_table[fdir_code]['actions']
        except:
            logger.error(f"No mitigation script found in the fdir table for fdir code {fdir_code}.")
            raise FdirException("Cannot find code in FDIR table")

        if priority <= self._priority:
            logger.warning(f"Received FDIR code with lower priority {fdir_code} ({priority}) "
                           f"than current state {self._state} ({self._priority}).")
            return

        self._state = fdir_code
        self._priority = priority

        # kill registered local scripts
        for pid in self._local_pids:
            try:
                process = psutil.Process(pid)
            except psutil.NoSuchProcess:
                logger.warning(
                    f"Could not find a process with PID {pid} @ localhost.")
            else:
                process.kill()
                logger.info(f"Killed registered script with PID {pid} @ localhost.")

        # Kill registered remote scripts
        for pid in self._remote_pids:
            response = self._remote_proxy.kill_process(pid)
            if isinstance(response, Success):
                logger.info(f"Killed registered script with PID {pid} @ {REMOTE_SETTINGS.HOSTNAME}.")
            else:
                logger.warning(
                    f"Could not kill process with PID {pid} @ {REMOTE_SETTINGS.HOSTNAME}.")

        # Clear all stored PIDs
        self._local_pids = []
        self._remote_pids = []

        # open filewriter for fdir script output logging
        timestring = datetime.now().strftime("%y-%m-%d_%H:%M:%S")
        outfilename = f"{self._logging_path}/log/{timestring}_fdir_{fdir_code}"
        os.makedirs(os.path.dirname(outfilename), exist_ok=True) # Create directories if they don't exist

        # create list of strings used to call subprocess
        exc_command = ["python3"]
        exc_command.append(recovery_command) # read script path
        exc_command[1] = f"{self._storage_path}{exc_command[1]}" # prepend path to script
        exc_command.extend(script_args) # add script arguments
        
        # run recovery script
        script_success = False
        try:
            outfile = open(outfilename, 'w')
            p = subprocess.Popen(exc_command,
                             stdout=outfile,
                             stderr=outfile,
                             shell=False,
                             preexec_fn=os.setpgrp)
            p.wait()
        except Exception as e:
            logger.error(f"failed to run {exc_command}: {e}")
        else:
            if p.returncode == 0:
                logger.info(f"Executed recovery script '{recovery_command}'.")
                script_success = True
            else:
                logger.info(f"Failed to execute script: '{recovery_command}'")
                script_success = False
        finally:
            outfile.close()

        # Create a single string representation of the actions list for the pop-up.
        action_string = "\n".join([f"- {action}" for action in actions])

        # Generate a pop-up on the remote machine (client).
        if self._remote_proxy.is_cs_connected():
            self._remote_proxy.generate_popup(
                code=fdir_code, actions=action_string, success=script_success)
        else:
            generate_popup(code=fdir_code, actions=action_string, success=script_success)

    def clear_fdir(self):
        self._priority = 0
        logger.info("Cleared FDIR state.")


    def get_state(self):
        return self._priority


def main():
    fmc = FdirManagerController()
    fmc.register_script('localhost', 11111)
    print("fdir_state =", fmc.get_state())
    fmc.signal_fdir('FDIR_TEST')
    fmc.signal_fdir('FDIR_TEST') # Should fail because of priority
    print("fdir_state =", fmc.get_state())
    fmc.clear_fdir()
    fmc.signal_fdir('FDIR_TEST')
    print("fdir_state =", fmc.get_state())

if __name__ == "__main__":
    main()
