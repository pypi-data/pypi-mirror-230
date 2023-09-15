import logging

from egse.command import ClientServerCommand
from egse.control import ControlServer
from egse.proxy import Proxy
from egse.protocol import CommandProtocol
from egse.settings import Settings
from egse.zmq_ser import connect_address, bind_address
from egse.system import format_datetime
from egse.fdir.fdir_remote_interface import FdirRemoteInterface
from egse.fdir.fdir_remote_controller import FdirRemoteController


logger = logging.getLogger(__name__)

CTRL_SETTINGS = Settings.load("FDIR Remote Control Server")
DEVICE_SETTINGS = Settings.load(filename="fdir_remote.yaml")
SITE_ID = Settings.load("SITE").ID


class FdirRemoteCommand(ClientServerCommand):
    pass


class FdirRemoteProxy(Proxy, FdirRemoteInterface):
    """ The FDIR Remote Proxy class is used to connect to the FDIR remote
        control server. It should only be used by the fdir manager.
    """

    def __init__(
        self,
        protocol=CTRL_SETTINGS.PROTOCOL,
        hostname=CTRL_SETTINGS.HOSTNAME,
        port=CTRL_SETTINGS.COMMANDING_PORT,
    ):
        super().__init__(connect_address(protocol, hostname, port))


class FdirRemoteProtocol(CommandProtocol):

    def __init__(self, control_server: ControlServer):

        super().__init__()

        self.control_server = control_server
        self.controller = FdirRemoteController()

        self.load_commands(
            DEVICE_SETTINGS.Commands,
            FdirRemoteCommand,
            FdirRemoteController,
        )

        self.build_device_method_lookup_table(self.controller)


    def get_bind_address(self):

        return bind_address(
            self.control_server.get_communication_protocol(),
            self.control_server.get_commanding_port(),
        )


    def get_status(self):

        return super().get_status()


    # The FDIR remote is stateless, so no HK.
    def get_housekeeping(self):

        return {"timestamp": format_datetime()}
