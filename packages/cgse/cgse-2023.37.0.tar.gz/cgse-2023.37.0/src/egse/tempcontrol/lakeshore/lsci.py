"""
Define the basic classes to access the LakeShore devices.
"""

import logging

from egse.decorators import dynamic_interface
from egse.device import DeviceInterface
from egse.proxy import Proxy
from egse.randomwalk import RandomWalk
from egse.settings import Settings
from egse.tempcontrol.lakeshore.lsci_devif import LakeShoreEthernetInterface
from egse.tempcontrol.lakeshore.lsci_devif import LakeShoreError
from egse.zmq_ser import connect_address

logger = logging.getLogger(__name__)

CTRL_SETTINGS = Settings.load("LakeShore Control Server")
LAKESHORE_SETTINGS = Settings.load("LakeShore Controller")
DEVICE_SETTINGS = Settings.load(filename="lsci.yaml")


class LakeShoreInterface(DeviceInterface):
    """
    The LakeShore base class.
    """
    @dynamic_interface
    def info(self) -> str:
        """
        Retrieve basic information about the LakeShore controller.
        :return: a multiline string with information about the device
        """
        raise NotImplementedError

    @dynamic_interface
    def get_id(self) -> str:
        """
        Returns lakeshore ID.

        Returns:
            The current ID: LS_X when X is the index of LakeShore.
        """
        raise NotImplementedError

    @dynamic_interface
    def get_temperature(self) -> float:
        """
        Retrieve the temperature from the given channel.

        Returns:
            The current temperature for the given channel.
        """
        raise NotImplementedError

    @dynamic_interface
    def get_params_pid(self, output:int) -> list:
        """
        Retrieve the PID Params.

        Returns:
            The params of P, I, D:
            Pos[0]: P
            Pos[1]: I
            Pos[2]: D
        """
        raise NotImplementedError

    @dynamic_interface
    def get_setpoint(self, output:int) -> float:
        """
        Retrieve the Setpoint Params.

        Returns:
            The setpoint:
        """
        raise NotImplementedError
    
    @dynamic_interface
    def get_tuning_status(self) -> list:
        """
        Returns the remote interface mode.

        Returns:
            Pos[0]: tuning status:  0 = no active tuning, 1 = active tuning.
            Pos[1]: output:         1 = output 1, 2 = output 2
            Pos[2]: error status:   0 = no tuning error, 1 = tuning error
            Pos[3]: stage status:   Specifies the current stage in the Autotune process.
        """
        raise NotImplementedError

    @dynamic_interface
    def get_heater_setup(self, output:int) -> list:
        """
        Return the Heater Setup Params.

        Returns:
            The params of Heater setup:
            Pos[0]: htr resistance
            Pos[1]: max current
            Pos[2]: max user current
            Pos[3]: current/power.
        """
        raise NotImplementedError
    
    @dynamic_interface
    def get_range(self, output:int) -> int:
        """
        Return the Range Params.

        Returns:
            The params of Range: 0 = Off, 1 = Low, 2 = Medium, 3 = High.
        """
        raise NotImplementedError

    @dynamic_interface
    def get_heater_status(self, output:int) -> int:
        """
        Return the Heater Status.

        Returns:
            The params of Heater setup: 0 = no error, 1 = heater open load, 2 = heater short
        """
        raise NotImplementedError

    @dynamic_interface
    def get_heater(self, output:int) -> float:
        """
        Return the Heater Value.

        Returns:
            The value of Heater
        """
        raise NotImplementedError

    @dynamic_interface
    def set_params_pid(self, output:int, p:int, i:int, d:int):
        """
        Configure the PID Params.
        """
        raise NotImplementedError
    
    @dynamic_interface
    def set_setpoint(self, output:int, value:str):
        """
        Configure the Setpoint Params.
        """
        raise NotImplementedError

    @dynamic_interface
    def set_autotune(self, output:int, mode:int):
        """
        Configure the AutoTune Params.
        """
        raise NotImplementedError

    @dynamic_interface
    def set_heater_setup(self,output:int, heater_resistant:int, max_current:int, max_user_current:str, output_display:int):
        """
        Configure the Heater Params.
        """
        raise NotImplementedError

    @dynamic_interface
    def set_range(self, output:int, range:int):
        """
        Configure the Range.
        """
        raise NotImplementedError


class LakeShoreSimulator(LakeShoreInterface):
    """
    The LakeShore controller Simulator class for Model .
    """

    def __init__(self):
        self._is_connected = True
        self._randomwalk = RandomWalk(start=15, boundary=(-100, 25), scale=0.01, count=0)
        self._p1_value = 1.2
        self._i1_value = 10.2
        self._d1_value = 50.0
        self._p2_value = 3.2
        self._i2_value = 13.2
        self._d2_value = 5.0
        self._setpoint = "125.3"
        self._heater_value = "25.3"

    def is_connected(self):
        return self._is_connected

    def is_simulator(self):
        return True

    def connect(self):
        self._is_connected = True

    def disconnect(self):
        self._is_connected = False

    def reconnect(self):
        if self.is_connected():
            self.disconnect()
        self.connect()

    def info(self):
        return "LSCI - The LakeShore Simulator"

    def get_id(self) -> str:
        return "LS_X"

    def get_temperature(self) -> float:
        return next(self._randomwalk)

    def get_params_pid(self, output:int) -> list:
        if output == 1:
            return [self._p1_value,self._i1_value,self._d1_value]
        elif output == 2:
            return [self._p2_value,self._i2_value,self._d2_value]
        else:
            return [0.0,0.0,0.0]
    
    def set_params_pid(self, output:int, p:int, i:int, d:int):
        if output == 1:
            self._p1_value = p
            self._i1_value = i
            self._d1_value = d
        elif output == 2:
            self._p2_value = p
            self._i2_value = i
            self._d2_value = d
        else:
            return

    def set_setpoint(self, output:int, value:str):
        self._setpoint = value
    
    def get_setpoint(self, output:int):
        return self._setpoint

    def get_heater(self, output:int):
        return self._heater_value


class LakeShoreController(LakeShoreInterface):
    """
    The LakeShore Controller class for Model .
    """

    def __init__(self, device_index):
        """Initialize the LakeShoreController interface."""

        super().__init__()

        device_id = f"LS_{device_index}"
        logger.debug(f"Initializing LakeShoreController {device_id} Model: 336")
        try:
            self.ls = LakeShoreEthernetInterface(device_index)
        except LakeShoreError as exc:
            logger.warning(f"LakeShoreError caught: Couldn't establish connection ({exc})")
            raise LakeShoreError(
                "Couldn't establish a connection with the LakeShore controller."
            ) from exc

    def connect(self):
        try:
            self.ls.connect()
        except LakeShoreError as exc:
            logger.warning(f"LakeShoreError caught: Couldn't establish connection ({exc})")
            raise ConnectionError(
                "Couldn't establish a connection with the LakeShore Controller."
            ) from exc

    def disconnect(self):
        try:
            self.ls.disconnect()
        except LakeShoreError as exc:
            raise ConnectionError("Couldn't disconnect from LakeShore Controller.") from exc

    def reconnect(self):
        if self.is_connected():
            self.disconnect()
        self.connect()

    def is_simulator(self):
        return False

    def is_connected(self):
        """Check if the LakeShore Controller is connected. """
        return self.ls.is_connected()

    def info(self) -> str:
        return self.ls.info()

    def get_id(self) -> str:
        return self.ls.get_id()

    def get_temperature(self) -> float:
        return self.ls.get_temperature()

    def get_params_pid(self, output:int) -> list:
        return self.ls.get_params_pid(output)

    def get_setpoint(self, output:int) -> float:
        return self.ls.get_setpoint(output)
    
    def get_tuning_status(self) -> list:
        return self.ls.get_tuning_status()

    def get_heater_setup(self, output:int) -> list:
        return self.ls.get_heater_setup(output)

    def get_heater_status(self, output:int) -> int:
        return self.ls.get_heater_status(output)

    def get_heater(self, output:int) -> float:
        return self.ls.get_heater(output)

    def get_range(self, output:int) -> int:
        return self.ls.get_range(output)

    def set_params_pid(self, output:int, p:int, i:int, d:int):
        self.ls.set_params_pid(output, p, i, d)

    def set_setpoint(self, output:int, value:str):
        self.ls.set_setpoint(output, value)

    def set_autotune(self, output:int, mode:int):
        self.ls.set_autotune(output, mode)

    def set_heater_setup(self,output:int, heater_resistant:int, max_current:int, max_user_current:str, output_display:int):
        self.ls.set_heater_setup(output, heater_resistant, max_current, max_user_current, output_display)

    def set_range(self, output:int, range:int):
        self.ls.set_range(output, range)


    def _get_response(self, cmd_string):
        response = self.ls.get_response(cmd_string)
        return response


class LakeShoreProxy(Proxy, LakeShoreInterface):
    """
    The LakeShoreProxy class is used to connect to the LakeShore control server and send commands
    to the LakeShore Hardware Controller remotely.
    """
    def __init__(self, lsci_index: int):
        self.name = "LS_"+str(lsci_index)
        protocol=CTRL_SETTINGS.PROTOCOL
        hostname=CTRL_SETTINGS.HOSTNAME
        port=CTRL_SETTINGS[self.name]["COMMANDING_PORT"]
        """
        Args:
            protocol: the transport protocol [default is taken from settings file]
            hostname: location of the control server (IP address)
                [default is taken from settings file]
            port: TCP port on which the control server is listening for commands
                [default is taken from settings file]
        """
        super().__init__(connect_address(protocol, hostname, port))
 