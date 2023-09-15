"""
The DPU Control Server will receive commands from the DPU Proxy and executes those commands via
the DPU Controller.

Start the DPU Control Server from the terminal as follows when you have the real hardware
connected via a Diagnostic SpaceWire Interface (DSI):
```bash
$ dpu_cs start [-a <IP address of DSI>] [-p <dsi port>]
```
Alternatively, when you want to run the FEE Simulator, start the DPU Control Server as follows:
```bash
$ dpu_cs start --zeromq
```
This last command will try to connect to an N-FEE simulator that is also started with the `--zeromq` option.
See the `feesim` module in `egse.fee` for more information.

Please note that software simulators are intended for simple test purposes and will not simulate
all device behavior correctly, e.g. timing, error conditions, etc.

"""
import getpass
import logging
import multiprocessing
import sys
import time

import click
import invoke
import rich
import sshtunnel
import zmq
from prometheus_client import start_http_server

from egse.control import ControlServer
from egse.control import is_control_server_active
from egse.dpu import DPUProtocol
from egse.dpu import DPUProxy
from egse.dsi.spw import SpaceWireOverDSI
from egse.settings import Settings
from egse.spw import SpaceWireInterface
from egse.zmq.spw import SpaceWireOverZeroMQ
from egse.zmq_ser import connect_address

logging.basicConfig(level=logging.DEBUG, format=Settings.LOG_FORMAT_PROCESS)

LOGGER = logging.getLogger(__name__)

DPU_SETTINGS = Settings.load("DPU")
DSI_SETTINGS = Settings.load("DSI")
SITE_SETTINGS = Settings.load("SITE")
CTRL_SETTINGS = Settings.load("DPU Control Server")


def is_dpu_cs_active(timeout: float = 0.5):
    """
    Checks whether the DPU Control Server is running.

    Args:
        timeout (float): Timeout when waiting for a reply [seconds, default=0.5]

    Returns:
        True if the DPU CS is running and replied with the expected answer.
    """

    endpoint = connect_address(
        CTRL_SETTINGS.PROTOCOL, CTRL_SETTINGS.HOSTNAME, CTRL_SETTINGS.COMMANDING_PORT
    )

    return is_control_server_active(endpoint, timeout)


class DPUControlServer(ControlServer):
    """
    The Control Server is the commanding center for the DPU. The CS receives commands from any
    DPU Proxy and puts them on a Queue for processing by the DPU Processor.
    """

    def __init__(self, transport: SpaceWireInterface):
        super().__init__()

        self.device_protocol = DPUProtocol(self, transport)

        self.logger.info(f"Binding ZeroMQ socket to {self.device_protocol.get_bind_address()}")

        self.device_protocol.bind(self.dev_ctrl_cmd_sock)

        self.poller.register(self.dev_ctrl_cmd_sock, zmq.POLLIN)

    def get_communication_protocol(self):
        return CTRL_SETTINGS.PROTOCOL

    def get_commanding_port(self):
        return CTRL_SETTINGS.COMMANDING_PORT

    def get_service_port(self):
        return CTRL_SETTINGS.SERVICE_PORT

    def get_monitoring_port(self):
        return CTRL_SETTINGS.MONITORING_PORT

    def get_storage_mnemonic(self):
        try:
            return CTRL_SETTINGS.STORAGE_MNEMONIC
        except AttributeError:
            return "DPU"

    def before_serve(self):
        start_http_server(CTRL_SETTINGS.METRICS_PORT)


def start_dpu_simulator(transport: SpaceWireInterface):

    multiprocessing.current_process().name = "dpu_cs"

    try:
        dpu_sim = DPUControlServer(transport)
        dpu_sim.serve()
    except KeyboardInterrupt:
        print("Shutdown requested...exiting")
    except SystemExit as exit_code:
        print("System Exit with code {}.".format(exit_code))
        return exit_code
    except Exception:
        import traceback

        traceback.print_exc(file=sys.stdout)


@click.group()
def cli():
    pass


@cli.command()
@click.option("--zeromq", is_flag=True,
              help="use ZeroMQ to connect to the DPU Processor")
@click.option("--dsi-address", "-a",
              help="the hostname or IP address of the DSI to which this client "
                   "will connect (+ tcp socket port)")
@click.option("--dsi-port", "-p", type=int, default=1,
              help="the DSI port number to which this client needs to connect "
                   "(not the port on the socket) [type=int]")
def start_bg(zeromq, dsi_address, dsi_port):
    """Start the DPU Control Server in the background."""

    if zeromq:
        options = "--zeromq"
    else:
        options = f"-a {dsi_address} " if dsi_address else ""
        options += f"-p {dsi_port}"

    LOGGER.info(f"Starting: dpu_cs start {options}")

    invoke.run(f"dpu_cs start {options}", disown=True)

    time.sleep(3.0)  # give the DPU CS and the DPU Processor the time to startup


@cli.command()
@click.option("--tunnel", is_flag=True,
              help="use an SSH tunnel to connect to the DSI")
@click.option("--zeromq", is_flag=True,
              help="use ZeroMQ to connect to the DPU Processor")
@click.option("--ssh-user", "-u",
              help="the username at the SSH server")
@click.option("--dsi-address", "-a",
              help="the hostname or IP address of the DSI to which this client "
                   "will connect (+ tcp socket port)")
@click.option("--dsi-port", "-p", type=int, default=1,
              help="the DSI port number to which this client needs to connect "
                   "(not the port on the socket) [type=int]")
def start(tunnel, zeromq, ssh_user, dsi_address, dsi_port):
    """
    Start the DPU Control Server and the DPU Processor.

    When --tunnel is specified, DSI_ADDRESS will default to 127.0.0.1
    unless explicitly provided.
    """

    if tunnel:
        user = getpass.getuser()
        password = getpass.getpass("Enter SSH passphrase: ")

        # This is the IP address of the SSH server.

        server_host = SITE_SETTINGS.SSH_SERVER
        server_port = SITE_SETTINGS.SSH_PORT

        # The IP address of the DSI, i.e. the EtherSpaceLink device from 4Links and
        # the default port as defined in the Settings configuration file.

        remote_host = DSI_SETTINGS.DSI_DPU_IP_ADDRESS
        remote_port = DSI_SETTINGS.DSI_DPU_PORT

        # The host from which the connection will be established. Usually, this
        # is the 'localhost', but can be specified on the commandline if needed.

        if not dsi_address:
            local_host = "127.0.0.1"
            local_port = 4949  # this number is just an arbitrary choice
            dsi_address = f"{local_host}:{local_port}"
        else:
            local_host, local_port = dsi_address.split(":")
            local_port = int(local_port)

        LOGGER.debug(
            f"SSH server: {server_host}:{server_port}, "
            f"DSI: {remote_host}:{remote_port}, "
            f"{local_host=}:{local_port=}, "
            f"{dsi_address=}, {dsi_port=}"
        )

        with sshtunnel.open_tunnel(
            (server_host, server_port),
            ssh_username=user,
            # FIXME: hardcoded info should go into specific user settings or the file should
            #   be searched for in the user's home directory.
            ssh_private_key="/Users/rik/.ssh/id_rsa",
            ssh_private_key_password=password,
            remote_bind_address=(remote_host, remote_port),
            local_bind_address=(local_host, local_port),
        ) as tunnel:
            transport = SpaceWireOverDSI(dsi_address, dsi_port)
            return start_dpu_simulator(transport)
    else:
        if zeromq:
            transport = SpaceWireOverZeroMQ("tcp://*:5555", "DPU--FEE")
        else:
            if not dsi_address:
                dsi_address = f"{DSI_SETTINGS.DSI_DPU_IP_ADDRESS}:{DSI_SETTINGS.DSI_DPU_PORT}"

            transport = SpaceWireOverDSI(dsi_address, dsi_port)

        return start_dpu_simulator(transport)


@cli.command()
def status():
    """Print the status of the control server."""

    import rich

    rich.print('DPU Control Server:')
    if is_dpu_cs_active():
        rich.print('  Status: [green]active')
        with DPUProxy() as proxy:
            rich.print(f"  Hostname: {proxy.get_ip_address()}")
            rich.print(f"  Monitoring port: {proxy.get_monitoring_port()}")
            rich.print(f"  Commanding port: {proxy.get_commanding_port()}")
            rich.print(f"  Service port: {proxy.get_service_port()}")
    else:
        rich.print('  Status: [red]not active')


@cli.command()
def stop():
    """Send a 'quit_server' command to the DPU Control Server."""

    if not is_dpu_cs_active():
        rich.print('DPU CS: [red]not active')
        return

    try:
        with DPUProxy() as proxy:
            sp = proxy.get_service_proxy()
            sp.quit_server()
    except ConnectionError:
        rich.print("[red]Couldn't connect to 'dpu_cs', process probably not running. ")


if __name__ == "__main__":
    sys.exit(cli())
