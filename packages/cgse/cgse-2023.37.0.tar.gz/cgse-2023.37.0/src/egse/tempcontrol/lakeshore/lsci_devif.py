import logging
import socket
import threading
import time

from egse.command import ClientServerCommand
from egse.settings import Settings
from egse.serialdevice import SerialDevice

MODULE_LOGGER = logging.getLogger(__name__)

LS_SETTINGS = Settings.load("LakeShore Controller")


class LakeShoreError(Exception):
    """Base exception for all LakeShore errors."""

    pass


class LakeShoreCommand(ClientServerCommand):
    def get_cmd_string(self, *args, **kwargs) -> str:
        out = super().get_cmd_string(*args, **kwargs)
        return out + "\n"

class LakeShoreEthernetInterface:
    def __init__(self, device_index):
        self.name = "LS_"+str(device_index)
        self.hostname = LS_SETTINGS[self.name]['HOSTNAME']
        self.port = LS_SETTINGS[self.name]['PORT']
        self.sock = None

        # Access-to-the-connection semaphore.
        # Use this to lock/unlock I/O access to the connection (whatever type it is) in
        # child classes.

        self.semaphore = threading.Semaphore()

        self.isConnectionOpen = False
        self.connect()

    def connect(self):

        # Sanity checks

        if self.isConnectionOpen:
            raise LakeShoreError("Socket is already open")
        if self.hostname in (None, ""):
            raise LakeShoreError("ERROR: hostname not initialized")
        if self.port in (None, 0):
            raise LakeShoreError("ERROR: port number not initialized")

        # Create a new socket instance

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # The following lines are to experiment with blocking and timeout, but there is no need.
            # self.sock.setblocking(1)
            # self.sock.settimeout(3)
        except socket.error as e_socket:
            raise LakeShoreError("ERROR: Failed to create socket.") from e_socket

        # Attempt to establish a connection to the remote host

        # FIXME: Socket shall be closed on exception?

        # We set a timeout of 3 sec before connecting and reset to None
        # (=blocking) after the connect. The reason for this is because when no
        # LakeShore is available, e.g during testing, the timeout will take about
        # two minutes which is way too long. It needs to be evaluated if this
        # approach is acceptable and not causing problems during production.

        try:
            MODULE_LOGGER.debug(
                f'Connecting a socket to host "{self.hostname}" using port {self.port}'
            )
            self.sock.settimeout(3)
            self.sock.connect((self.hostname, self.port))
            self.sock.settimeout(None)
        except ConnectionRefusedError as e_cr:
            raise LakeShoreError(f"ERROR: Connection refused to {self.hostname}") from e_cr
        except TimeoutError as e_timeout:
            raise LakeShoreError(f"ERROR: Connection to {self.hostname} timed out") from e_timeout
        except socket.gaierror as e_gai:
            raise LakeShoreError(f"ERROR: socket address info error for {self.hostname}") from e_gai
        except socket.herror as e_h:
            raise LakeShoreError(f"ERROR: socket host address error for {self.hostname}") from e_h
        except socket.timeout as e_timeout:
            raise LakeShoreError(f"ERROR: socket timeout error for {self.hostname}") from e_timeout
        except OSError as ose:
            raise LakeShoreError(f"ERROR: OSError caught ({ose}).") from ose

        self.isConnectionOpen = True

        # Check that we are connected to a pmac by issuing the "VERSION" command --
        # expecting the 1.947 in return.
        # If we don't get the right response, then disconnect automatically

        if not self.is_connected():
            raise LakeShoreError("Device is not connected, check logging messages for the cause.")

    def disconnect(self):
        """
        Disconnect from the Ethernet connection.

        Raises a LakeShoreError on failure.
        """
        try:
            if self.isConnectionOpen:
                MODULE_LOGGER.debug(f"Disconnecting from {self.hostname}")
                self.semaphore.acquire()
                self.sock.close()
                self.semaphore.release()
                self.isConnectionOpen = False
        except Exception as e_exc:
            raise LakeShoreError(f"Could not close socket to {self.hostname}") from e_exc

    def is_connected(self):

        if not self.isConnectionOpen:
            return False

        try:
            response = self.get_response("*IDN?\n")
        except LakeShoreError as e_lakeshore:
            if len(e_lakeshore.args) >= 2 and e_lakeshore.args[1] == -1:
                MODULE_LOGGER.error(
                    f"While trying to talk to the device the following exception occurred, "
                    f"exception={e_lakeshore}"
                )
                MODULE_LOGGER.error(
                    "Most probably the client connection was closed. Disconnecting..."
                )
                self.disconnect()
                return False
            else:
                MODULE_LOGGER.error(
                    f"While trying to talk to the device the following exception occurred, "
                    f"exception={e_lakeshore}"
                )
                self.disconnect()
                return False
        finally:
            pass

        version = response

        if not version.startswith("LSCI"):
            # if the response string doesn't start with LSCI then we're not talking to a
            # LakeShore device!
            MODULE_LOGGER.error(
                f'Device did not respond correctly to a "VERSION" command, response={response}. '
                f"Disconnecting..."
            )
            self.disconnect()
            return False

        return True

    def get_response(self, command: str, wait=True)-> str:
        """
        Send a single command to the controller and block until a response from the controller.

        :param str command: is the command to be sent

        :param bool wait: whether to wait on the semaphore [default = True].

            This should normally be left default. If we have acquired the semaphore manually,
            then specify wait = False (and don't forget to release the semaphore eventually).

        :return: either a string returned by the PMAC (on success), or an error message (on failure)

        :raises: LakeShoreError when there was an I/O problem during comm with the PMAC or
        the response does
                 not have recognised terminators.
        """

        try:
            if wait:
                self.semaphore.acquire()

            # Attempt to send the complete command

            self.sock.sendall(command.encode())

            # wait for, read and return the response from HUBER (will be at most TBD chars)

            return_string = self.wait_for_response()

            return return_string.decode().replace("\r\n", "").replace("+","")
        
        except socket.timeout as e_timeout:
            raise LakeShoreError("Socket timeout error") from e_timeout
        except socket.error as e_socket:
            # Interpret any socket-related error as an I/O error
            raise LakeShoreError("Socket communication error.") from e_socket
        finally:
            if wait:
                self.semaphore.release()

    def write(self, command: str):
        """
        Send a single command to the device controller without waiting for a response.

        Args:
            command: an order command for the controller.

        Raises:
            DeviceConnectionError when the command could not be sent due to a
            communication problem.

            DeviceTimeoutError when the command could not be sent due to a timeout.
        """

        try:
            self.sock.sendall(command.encode())

        except socket.timeout as e_timeout:
            raise LakeShoreError("Socket timeout error") from e_timeout
        except socket.error as e_socket:
            # Interpret any socket-related error as a connection error
            raise LakeShoreError("Socket communication error.") from e_socket
        except AttributeError:
            if not self.is_connected:
                msg = "The LakeShore is not connected, use the connect() method."
                raise LakeShoreError(msg)
            raise

    def wait_for_response(self):
        n_total = 0
        buf_size = 2048

        try:
            for idx in range(100):
                time.sleep(0.05)  # Give the device time to fill the buffer
                data = self.sock.recv(buf_size)
                n = len(data)
                n_total += n
                if n < buf_size:
                    break
        except socket.timeout as e_timeout:
            MODULE_LOGGER.warning(f"Socket timeout error from {e_timeout}")
            return b"\r\n"

       # MODULE_LOGGER.debug(f"Total number of bytes received is {n_total}, idx={idx}")

        return data

    def info(self):
        return self.get_response("*IDN?\n")
    
    def get_id(self):
        return self.name
    
    def get_temperature(self):
        return self.get_response("CRDG? A\n")

    def get_params_pid(self, output:int):
        return self.get_response(f"PID? {output}\n").split(",")

    def get_setpoint(self, output:int):
        return self.get_response(f"SETP? {output}\n",)
    
    def get_tuning_status(self):
        return self.get_response(f"TUNEST?\n").split(",")
    
    def get_heater_setup(self, output:int):
        return self.get_response(f"HTRSET? {output}\n").split(",")
    
    def get_range(self, output:int):
        return self.write(f"RANGE? {output}\n")
    
    def get_heater_status(self, output:int):
        return self.get_response(f"HTRST? {output}\n")
    
    def get_heater(self, output:int):
        return self.get_response(f"HTR? {output}\n",)
    
    def set_params_pid(self, output:int, p:int, i:int, d:int):
        self.write(f"PID {output} {p} {i} {d}\n")

    def set_setpoint(self, outpout:int, value:str):
        self.write(f"SETP {outpout},{value}\n")

    def set_autotune(self, output:int, mode:int):
        self.write(f"ATUNE {output},{mode}\n")

    def set_heater_setup(self,output:int, heater_resistant:int, max_current:int, max_user_current:str, output_display:int):
        self.write(f"HTRSET {output},{heater_resistant},{max_current},{max_user_current},{output_display}\n")

    def set_range(self, output:int, range:int):
        self.write(f"RANGE {output},{range}\n")