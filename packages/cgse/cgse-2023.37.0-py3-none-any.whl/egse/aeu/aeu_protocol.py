import logging

from egse.aeu import aeu_metrics
from egse.aeu.aeu import SyncData
from egse.command import ClientServerCommand
from egse.control import ControlServer
from egse.device import DeviceConnectionError, DeviceConnectionState
from egse.device import DeviceTimeoutError
from egse.hk import read_conversion_dict, convert_hk_names
from egse.protocol import CommandProtocol
from egse.settings import Settings
from egse.state import GlobalState
from egse.system import format_datetime, SignalCatcher
from egse.zmq_ser import bind_address

logger = logging.getLogger(__name__)

CRIO_SETTINGS = Settings.load(filename="aeu_crio.yaml")
PSU_SETTINGS = Settings.load(filename="aeu_psu.yaml")
AWG_SETTINGS = Settings.load(filename="aeu_awg.yaml")

LINE_FEED = "\x0A"
CARRIAGE_RETURN = "\x0D"


POWERLINES = {1: "CCD", 2: "CLK", 3: "AN1", 4: "AN2", 5: "AN3", 6: "DIG"}


########################
# Client-server commands
########################


class CRIOCommand(ClientServerCommand):
    """ Client-server command for the AEU cRIO."""

    def get_cmd_string(self, *args, **kwargs) -> str:
        """ Return the command string.

        All commands must be terminated using a valid terminator code 0x0D (Carriage Return, CR), followed by a 0x0A
        (Line Feed, LF).  See PTO-EVO-SYS-UCD-0188-2B (PLATO-AEU CAM TEST EGSE TMTC ICD).

        Args:
            - args: Positional arguments for the command.
            - kwargs: Keyword arguments for the command.

        Returns: Command string for the cRIO.
        """

        cmd_string = super().get_cmd_string(*args, **kwargs)

        return cmd_string + CARRIAGE_RETURN + LINE_FEED


class PSUCommand(ClientServerCommand):
    """ Client-server command for the AEU PSU."""

    def get_cmd_string(self, *args, **kwargs) -> str:
        """ Return the command string.

        All commands must be terminated using a valid terminator code 0x0A (Line Feed, LF).  See
        PTO-EVO-SYS-UCD-0188-2B (PLATO-AEU CAM TEST EGSE TMTC ICD).

        Args:
            - args: Positional arguments for the command.
            - kwargs: Keyword arguments fort the command.

        Returns: Command string for the PSU.
        """

        cmd_string = super().get_cmd_string(*args, **kwargs)

        return cmd_string + LINE_FEED


class AWGCommand(ClientServerCommand):
    """ Client-server command for the AEU AWG."""

    def get_cmd_string(self, *args, **kwargs) -> str:
        """ Return the command string.

        All commands must be terminated with the command terminator code 0x0A (Line Feed, LF), except for ARB1, ARB2,
        ARB3, ARB4, ARB1?, ARB2?, ARB3?, and ARB4? commands.  See PTO-EVO-SYS-UCD-0188-2B (PLATO-AEU CAM TEST EGSE TMTC
        ICD).

        Args:
            - args: Positional arguments for the command.
            - kwargs: Keyword arguments fort the command.

        Returns: Command string for the AWG.
        """

        cmd_string = super().get_cmd_string(*args, **kwargs)

        if not (cmd_string.startswith("ARB1") or cmd_string.startswith("ARB2") or cmd_string.startswith("ARB3")
                or cmd_string.startswith("ARB4")):

            cmd_string += LINE_FEED

        return cmd_string

###########
# Protocols
###########


class AEUProtocol(CommandProtocol):
    """ AEU protocol."""

    def __init__(self, control_server: ControlServer):
        """ Initialisation of an AEU protocol with the given Control Server.

        Args:
            - control_server: Control Server to associate the AEU protocol with.
        """

        super().__init__()

        self.control_server = control_server

    def get_bind_address(self):
        """ Return the address for the AEU protocol to bind to.

        Returns: Address for the AEU protocol to bind to.
        """

        return bind_address(self.control_server.get_communication_protocol(), self.control_server.get_commanding_port())

    def get_status(self):
        """ Return the status information.

        Returns: Status information.
        """

        status = super(AEUProtocol, self).get_status()

        return status

    def get_housekeeping(self) -> dict:
        """ Return the housekeeping.

        Returns: Dictionary with the housekeeping.
        """

        hk = {"timestamp": format_datetime()}

        return hk


class CRIOProtocol(AEUProtocol):

    def __init__(self, control_server: ControlServer):
        """ Initialisation of a cRIO protocol with the given Control Server.

        Args:
            - control_server: Control Server to associate the cRIO protocol with.
        """

        super(CRIOProtocol, self).__init__(control_server)

        self.hk_conversion_table = read_conversion_dict(self.control_server.get_storage_mnemonic(), use_site=False)

        if Settings.simulation_mode():

            # Simulation mode -> start the simulator

            from egse.aeu.aeu import CRIOSimulator
            self.crio = CRIOSimulator()

        else:

            # Device available -> start the controller

            from egse.aeu.aeu import CRIOController
            self.crio = CRIOController()
            self.crio.add_observer(self)

        # Connect to the simulator/controller

        try:

            self.crio.connect()

        except (ConnectionError, DeviceConnectionError, DeviceTimeoutError) as exc:

            logger.warning(f"Couldn't connect to cRIO: {exc}")

        # Load the commands

        from egse.aeu.aeu import CRIOInterface
        self.load_commands(CRIO_SETTINGS.Commands, CRIOCommand, CRIOInterface)

        # Build the method look-up table

        self.build_device_method_lookup_table(self.crio)

    def get_status(self):
        """ Return the status information.

        Returns: Status information.
        """

        status_info = super().get_status()

        led_status = self.crio.get_led_status()

        status_info.update(led_status)

        if led_status["N-CAM"]:

            # status_info["Camera"] = "N"

            clk_50mhz, clk_ccdread = self.crio.get_n_cam_clock_status()

            status_info["Clk_N_50MHz"] = clk_50mhz
            status_info["Clk_N_ccdread"] = clk_ccdread

        elif led_status["F-CAM"]:

            # status_info["Camera"] = "F"

            clk_50mhz_nom, clk_50_mhz_red, clk_ccdread_nom, clk_ccdread_red = self.crio.get_f_cam_clock_status()

            status_info["Clk_F_50MHz_nom"] = clk_50mhz_nom
            status_info["Clk_F_50MHz_red"] = clk_50_mhz_red
            status_info["Clk_F_ccdread_nom"] = clk_ccdread_nom
            status_info["Clk_F_ccdread_red"] = clk_ccdread_red

        clk_50mhz_nom, clk_50_mhz_red, clk_heater_nom, clk_heater_red = self.crio.get_svm_clock_status()

        status_info["Clk_TCS_50MHz_nom"] = clk_50mhz_nom
        status_info["Clk_TCS_50MHz_red"] = clk_50_mhz_red
        status_info["Clk_heater_nom"] = clk_heater_nom
        status_info["Clk_heater_red"] = clk_heater_red

        return status_info

    def get_housekeeping(self) -> dict:
        """ Return the housekeeping.

        Returns: Dictionary with the housekeeping.
        """

        hk = super().get_housekeeping()

        if self.state == DeviceConnectionState.DEVICE_CONNECTED or Settings.simulation_mode():

            crio_data = self.crio.get_data()
            crio_data = convert_hk_names(crio_data, self.hk_conversion_table)

            aeu_metrics.GAEU_I_CCD_NFEE.set(crio_data[f"GAEU_I_CCD_NFEE"])
            aeu_metrics.GAEU_I_CLK_NFEE.set(crio_data[f"GAEU_I_CLK_NFEE"])
            aeu_metrics.GAEU_I_AN1_NFEE.set(crio_data[f"GAEU_I_AN1_NFEE"])
            aeu_metrics.GAEU_I_AN2_NFEE.set(crio_data[f"GAEU_I_AN2_NFEE"])
            aeu_metrics.GAEU_I_AN3_NFEE.set(crio_data[f"GAEU_I_AN3_NFEE"])
            aeu_metrics.GAEU_I_DIG_NFEE.set(crio_data[f"GAEU_I_DIG_NFEE"])

            aeu_metrics.GAEU_V_CCD_NFEE.set(crio_data[f"GAEU_V_CCD_NFEE"])
            aeu_metrics.GAEU_V_CLK_NFEE.set(crio_data[f"GAEU_V_CLK_NFEE"])
            aeu_metrics.GAEU_V_AN1_NFEE.set(crio_data[f"GAEU_V_AN1_NFEE"])
            aeu_metrics.GAEU_V_AN2_NFEE.set(crio_data[f"GAEU_V_AN2_NFEE"])
            aeu_metrics.GAEU_V_AN3_NFEE.set(crio_data[f"GAEU_V_AN3_NFEE"])
            aeu_metrics.GAEU_V_DIG_NFEE.set(crio_data[f"GAEU_V_DIG_NFEE"])

            aeu_metrics.GAEU_I_CCD_FFEE.set(crio_data[f"GAEU_I_CCD_FFEE"])
            aeu_metrics.GAEU_I_CLK_FFEE.set(crio_data[f"GAEU_I_CLK_FFEE"])
            aeu_metrics.GAEU_I_AN1_FFEE.set(crio_data[f"GAEU_I_AN1_FFEE"])
            aeu_metrics.GAEU_I_AN2_FFEE.set(crio_data[f"GAEU_I_AN2_FFEE"])
            aeu_metrics.GAEU_I_AN3_FFEE.set(crio_data[f"GAEU_I_AN3_FFEE"])
            aeu_metrics.GAEU_I_DIG_FFEE.set(crio_data[f"GAEU_I_DIG_FFEE"])

            aeu_metrics.GAEU_V_CCD_FFEE.set(crio_data[f"GAEU_V_CCD_FFEE"])
            aeu_metrics.GAEU_V_CLK_FFEE.set(crio_data[f"GAEU_V_CLK_FFEE"])
            aeu_metrics.GAEU_V_AN1_FFEE.set(crio_data[f"GAEU_V_AN1_FFEE"])
            aeu_metrics.GAEU_V_AN2_FFEE.set(crio_data[f"GAEU_V_AN2_FFEE"])
            aeu_metrics.GAEU_V_AN3_FFEE.set(crio_data[f"GAEU_V_AN3_FFEE"])
            aeu_metrics.GAEU_V_DIG_FFEE.set(crio_data[f"GAEU_V_DIG_FFEE"])

            aeu_metrics.GAEU_STANDBY.set(int(crio_data["GAEU_STANDBY"]))
            aeu_metrics.GAEU_SELFTEST.set(int(crio_data["GAEU_SELFTEST"]))
            aeu_metrics.GAEU_FC_TVAC.set(int(crio_data["GAEU_FC_TVAC"]))
            aeu_metrics.GAEU_ALIGNMENT.set(int(crio_data["GAEU_ALIGNMENT"]))

            aeu_metrics.GAEU_PWR_NFEE_STATUS.set(int(crio_data["GAEU_PWR_NFEE_STATUS"]))
            aeu_metrics.GAEU_PWR_FFEE_STATUS.set(int(crio_data["GAEU_PWR_FFEE_STATUS"]))

            aeu_metrics.GAEU_PWR_CCD_FEE_STATUS.set(int(crio_data["GAEU_PWR_CCD_FEE_STATUS"]))
            aeu_metrics.GAEU_PWR_CLK_FEE_STATUS.set(int(crio_data["GAEU_PWR_CLK_FEE_STATUS"]))
            aeu_metrics.GAEU_PWR_AN1_FEE_STATUS.set(int(crio_data["GAEU_PWR_AN1_FEE_STATUS"]))
            aeu_metrics.GAEU_PWR_AN2_FEE_STATUS.set(int(crio_data["GAEU_PWR_AN2_FEE_STATUS"]))
            aeu_metrics.GAEU_PWR_AN3_FEE_STATUS.set(int(crio_data["GAEU_PWR_AN3_FEE_STATUS"]))
            aeu_metrics.GAEU_PWR_DIG_FEE_STATUS.set(int(crio_data["GAEU_PWR_DIG_FEE_STATUS"]))

            aeu_metrics.GAEU_S_VOLTAGE_OOR.set(int(crio_data["GAEU_S_VOLTAGE_OOR"]))
            aeu_metrics.GAEU_S_CURRENT_OOR.set(int(crio_data["GAEU_S_CURRENT_OOR"]))
            aeu_metrics.GAEU_SYNC_GF.set(int(crio_data["GAEU_SYNC_GF"]))

            aeu_metrics.GAEU_CLK_PWR_50MHZ.set(int(crio_data["GAEU_CLK_PWR_50MHZ"]))
            aeu_metrics.GAEU_CLK_PWR_CCDREAD.set(int(crio_data["GAEU_CLK_PWR_CCDREAD"]))
            aeu_metrics.GAEU_CLK_PWR_SVM.set(int(crio_data["GAEU_CLK_PWR_SVM"]))
            aeu_metrics.GAEU_CLK_PWR_N_FFEE.set(int(crio_data["GAEU_CLK_PWR_N_FFEE"]))
            aeu_metrics.GAEU_CLK_PWR_R_FFEE.set(int(crio_data["GAEU_CLK_PWR_R_FFEE"]))
            aeu_metrics.GAEU_TESTPORT.set(int(crio_data["GAEU_TESTPORT"]))

            hk.update(crio_data)

        return hk


class PSUProtocol(AEUProtocol):

    def __init__(self, control_server: ControlServer, psu_index: int):
        """ Initialisation of a PSU protocol with the given Control Server and index.

        Args:
            - control_server: Control Server to associate the PSU protocol with.
            - psu_index: Index of the PSU (should be 1..6).
        """

        super(PSUProtocol, self).__init__(control_server)

        self.psu_index = psu_index
        self.name = POWERLINES[self.psu_index]

        if Settings.simulation_mode():

            # Simulation mode -> start the simulator

            from egse.aeu.aeu import PSUSimulator
            self.psu = PSUSimulator(psu_index)

        else:

            # Device available -> start the controller

            from egse.aeu.aeu import PSUController
            self.psu = PSUController(psu_index)
            self.psu.add_observer(self)

        # Connect to the simulator/controller

        try:
            self.psu.connect()
        except (ConnectionError, DeviceConnectionError, DeviceTimeoutError) as exc:
            logger.warning(f"Couldn't connect to cRIO: {exc}")

        # Load the commands

        from egse.aeu.aeu import PSUInterface
        self.load_commands(PSU_SETTINGS.Commands, PSUCommand, PSUInterface)

        # Build the method look-up table

        self.build_device_method_lookup_table(self.psu)

    def get_housekeeping(self) -> dict:
        """ Return the housekeeping and update the metrics.

        Returns: Dictionary with the housekeeping.
        """

        hk = super().get_housekeeping()

        current = self.psu.get_current()
        voltage = self.psu.get_voltage()

        hk[f"GAEU_PSU_I_{self.name}"] = current
        hk[f"GAEU_PSU_V_{self.name}"] = voltage

        if self.name == "CCD":
            aeu_metrics.GAEU_PSU_V_CCD.set(voltage)
            aeu_metrics.GAEU_PSU_I_CCD.set(current)
        elif self.name == "CLK":
            aeu_metrics.GAEU_PSU_V_CLK.set(voltage)
            aeu_metrics.GAEU_PSU_I_CLK.set(current)
        elif self.name == "AN1":
            aeu_metrics.GAEU_PSU_V_AN1.set(voltage)
            aeu_metrics.GAEU_PSU_I_AN1.set(current)
        elif self.name == "AN2":
            aeu_metrics.GAEU_PSU_V_AN2.set(voltage)
            aeu_metrics.GAEU_PSU_I_AN2.set(current)
        elif self.name == "AN3":
            aeu_metrics.GAEU_PSU_V_AN3.set(voltage)
            aeu_metrics.GAEU_PSU_I_AN3.set(current)
        elif self.name == "DIG":
            aeu_metrics.GAEU_PSU_V_DIG.set(voltage)
            aeu_metrics.GAEU_PSU_I_DIG.set(current)

        return hk


class AWGProtocol(AEUProtocol):

    def __init__(self, control_server: ControlServer, awg_index: int):
        """ Initialisation of an AWG protocol with the given Control Server and index.

        Args:
            - control_server: Control Server to associate the AWG protocol with.
            - awg_index: Index of the AWG (should be 1 or 2).
        """

        super(AWGProtocol, self).__init__(control_server)

        self.awg_index = awg_index

        self.killer = SignalCatcher()

        if Settings.simulation_mode():

            # Simulation mode -> start the simulator

            from egse.aeu.aeu import AWGSimulator
            self.awg = AWGSimulator(awg_index)

        else:

            # Device available -> start the controller

            from egse.aeu.aeu import AWGController
            self.awg = AWGController(awg_index)
            self.awg.add_observer(self)

        # Connect to the simulator/controller

        try:
            self.awg.connect()
        except (ConnectionError, DeviceConnectionError, DeviceTimeoutError) as exc:
            logger.warning(f"Couldn't connect to cRIO: {exc}")

        # Load the commands

        from egse.aeu.aeu import AWGInterface
        self.load_commands(AWG_SETTINGS.Commands, AWGCommand, AWGInterface)

        # Build the method look-up table

        self.build_device_method_lookup_table(self.awg)

        self.setup = GlobalState.setup

    def get_housekeeping(self) -> dict:
        """ Return the housekeeping.

        Returns: Dictionary with the housekeeping.
        """

        hk = super().get_housekeeping()

        # For AWG2, we use ARBDEF1 to configure Clk_ccdread.  The name of ARBDEF1 for AWG2 (CCDREAD<identifier>)
        # contains an identifier, which can be used to determine the image cycle time (for external sync mode).

        if self.awg_index == 2 and (self.state == DeviceConnectionState.DEVICE_CONNECTED or Settings.simulation_mode()):

            arbdef_name = self.awg.get_arb1_def()[0]    # Name of ARBDEF1

            sync_data_string = self.setup.gse.aeu.awg2.calibration.n_cam_sync_data[arbdef_name[-1]]
            image_cycle_time = SyncData(sync_data_string).image_cycle_time

            hk["GAEU_EXT_CYCLE_TIME"] = image_cycle_time

            aeu_metrics.GAEU_EXT_CYCLE_TIME.set(image_cycle_time)

        return hk
