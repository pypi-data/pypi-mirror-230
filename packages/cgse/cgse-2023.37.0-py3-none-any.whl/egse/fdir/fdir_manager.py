import logging

from prometheus_client import Gauge

from egse.command import ClientServerCommand
from egse.control import ControlServer
from egse.proxy import Proxy
from egse.protocol import CommandProtocol
from egse.settings import Settings
from egse.zmq_ser import connect_address, bind_address
from egse.system import format_datetime
from egse.fdir.fdir_manager_interface import FdirManagerInterface
from egse.fdir.fdir_manager_controller import FdirManagerController

logger = logging.getLogger(__name__)

CTRL_SETTINGS = Settings.load("FDIR Manager Control Server")
DEVICE_SETTINGS = Settings.load(filename="fdir_manager.yaml")
SITE_ID = Settings.load("SITE").ID

gauge_state = Gauge(f"G{SITE_ID}_FDIR_STATE", "")


class FdirManagerCommand(ClientServerCommand):
    pass



class FdirManagerProxy(Proxy, FdirManagerInterface):
    """ The FDIR Manager Proxy class is used to connect to the FDIR Manager
        control server and send commands and requests for the FDIR manager.
    """

    def __init__(
        self,
        protocol=CTRL_SETTINGS.PROTOCOL,
        hostname=CTRL_SETTINGS.HOSTNAME,
        port=CTRL_SETTINGS.COMMANDING_PORT,
    ):
        super().__init__(connect_address(protocol, hostname, port))


class FdirManagerProtocol(CommandProtocol):

    def __init__(self, control_server: ControlServer):

        super().__init__()

        self.control_server = control_server
        self.controller = FdirManagerController()

        self.load_commands(
            DEVICE_SETTINGS.Commands,
            FdirManagerCommand,
            FdirManagerController,
        )

        self.build_device_method_lookup_table(self.controller)


    def get_bind_address(self):

        return bind_address(
            self.control_server.get_communication_protocol(),
            self.control_server.get_commanding_port(),
        )


    def get_status(self):

        status = super().get_status()
        status.update({"state": self.controller.get_state()})

        return status


    def get_housekeeping(self):

        state = self.controller.get_state()
        gauge_state.set(state)

        return {
            "timestamp": format_datetime(),
            f"G{SITE_ID}_FDIR_STATE": state,
        }
