"""
For each hardware component of the AEU (i.e. cRIO, PSU[1:6], and AEG[1:2]), a Control Server that connects to that
hardware component must be started.  With this module, you can start and shut down these Control Servers all in one go,
or one-by-one.  In absence of the real hardware, the Control Servers can be started in simulator mode.

To start all AEU control servers from the terminal:

    ```bash
        $ aeu_cs start [--sim]
    ```

The `--sim` option must be used to start the Control Servers in simulator mode (e.g. in absence of the real hardware).

To shut down all Control Servers from the terminal:

    ```bash
        $ aeu_cs stop
    ```

Individual AEU Control Servers can be started from the terminal as follows:

    ```bash
        $ aeu_cs start-crio-cs [--sim]

        $ aeu_cs start-psu-cs 1 [--sim]
        $ aeu_cs start-psu-cs 2 [--sim]
        $ aeu_cs start-psu-cs 3 [--sim]
        $ aeu_cs start-psu-cs 4 [--sim]
        $ aeu_cs start-psu-cs 5 [--sim]
        $ aeu_cs start-psu-cs 6 [--sim]

        $ aeu_cs start-awg-cs 1 [--sim]
        $ aeu_cs start-awg-cs 2 [--sim]
    ```

Also here the `--sim` option must be used to start the control servers in simulator mode (e.g. in absence of the real
hardware).

To shut down individual Control Servers from the terminal:

    ```bash
        $ aeu_cs stop-crio-cs

        $ aeu_cs stop-psu-cs 1
        $ aeu_cs stop-psu-cs 2
        $ aeu_cs stop-psu-cs 3
        $ aeu_cs stop-psu-cs 4
        $ aeu_cs stop-psu-cs 5
        $ aeu_cs stop-psu-cs 6

        $ aeu_cs stop-awg-cs 1
        $ aeu_cs stop-awg-cs 2
    ```
"""

import logging
import multiprocessing

import sys

from egse.state import GlobalState
from egse.system import SignalCatcher

multiprocessing.current_process().name = "aeu_cs"

import click
import rich
import zmq
from invoke import run
from prometheus_client import start_http_server

from egse.aeu.aeu import CRIOProxy, is_aeu_cs_active, PSUProxy, AWGProxy
from egse.aeu.aeu_protocol import CRIOProtocol, PSUProtocol, AWGProtocol
from egse.control import ControlServer
from egse.settings import Settings

logger = logging.getLogger(__name__)

CTRL_SETTINGS = Settings.load("AEU Control Server")


class AEUControlServer(ControlServer):
    """ AEUControlServer - Command and monitor the AEU EGSE hardware.

    This class works as a command and monitoring server to control an AEU EGSE device. This Control Server shall be used
    as the single-point access for controlling the hardware device. Monitoring access should be done preferably through
    this Control Server also.

    The sever binds to the following ZeroMQ sockets:

        - REQ-REP socket that can be used as a command server. Any client can connect and send a command to the AEU EGSE
          device.
        - PUB-SUP socket that serves as a monitoring server. It will send out AEU EGSE device status information to all
          the connected clients every TBD seconds.
    """

    def __init__(self, name: str):
        """ Initialisation of an AEU Control Server with the given name.

        Args:
            - name: Name of the AEU hardware component.
        """

        self.name = name

        super(AEUControlServer, self).__init__()

        self.device_protocol = None
        self.set_protocol()

        self.logger.info(f"Binding ZeroMQ socket to {self.device_protocol.get_bind_address()}")
        self.device_protocol.bind(self.dev_ctrl_cmd_sock)

        self.poller.register(self.dev_ctrl_cmd_sock, zmq.POLLIN)

        self.set_delay(CTRL_SETTINGS[name]["DELAY"])
        self.set_hk_delay(CTRL_SETTINGS[name]["HK_DELAY"])

    def get_communication_protocol(self):
        """ Return the communication protocol.

        Return the communication protocol as mentioned in the settings file.  This is the same for AEU Control Servers.

        Returns: Communication protocol.
        """

        return CTRL_SETTINGS.PROTOCOL

    def get_commanding_port(self):
        """ Return the commanding port.

        Return the commanding port as mentioned in the settings file.  This is different for all AEU Control Servers.

        Returns: Commanding port.
        """

        return CTRL_SETTINGS[self.name]["COMMANDING_PORT"]

    def get_service_port(self):
        """Return the service port.

        Return the service port as mentioned in the settings file.  This is different for all AEU Control Servers.

        Returns: Service port.
        """

        return CTRL_SETTINGS[self.name]["SERVICE_PORT"]

    def get_monitoring_port(self):
        """ Return the monitoring port.

        Return the monitoring port as mentioned in the settings file.  This is different for all AEU Control Servers.

        Returns: Monitoring port.
        """

        return CTRL_SETTINGS[self.name]["MONITORING_PORT"]

    def get_metrics_port(self):
        """ Return the metrics port.

        Return the metrics port as mentioned in the settings file.  This is different for all AEU Control Servers.

        Returns: Metrics port.
        """

        return CTRL_SETTINGS[self.name]["METRICS_PORT"]

    def get_storage_mnemonic(self):
        """ Return the storage mnemonic.

        Return the storage mnemonic as mentioned in the settings file.  If this is not mentioned there, the name of the
        AEU device is used.

        Returns: Storage mnemonic.
        """

        try:

            return CTRL_SETTINGS[self.name]["STORAGE_MNEMONIC"]

        except AttributeError:

            return self.name

    def before_serve(self):
        """ Start the HTTP server for monitoring with Prometheus and Grafana."""

        start_http_server(CTRL_SETTINGS[self.name]["METRICS_PORT"])

    def set_protocol(self):
        """ Set the protocol for the AEU Control Server.

        This should be implemented in the component-specific classes.
        """

        pass


class CRIOControlServer(AEUControlServer):
    """ AEU Control Server for the cRIO."""

    def __init__(self):
        """ Initialisation of an AEU Control Server for the cRIO."""

        super().__init__("CRIO")

    def set_protocol(self):
        """ Set the protocol for the cRIO Control Server."""

        self.device_protocol = CRIOProtocol(self)


class PSUControlServer(AEUControlServer):
    """ AEU Control Server for the PSU."""

    def __init__(self, psu_index: int):
        """ Initialisation of an AEU Control Server for the PSU with the given index.

        Args:
            - psu_index: Index of the PSU (should be 1..6).
        """

        self.psu_index = psu_index

        super().__init__("PSU" + str(psu_index))

    def set_protocol(self):
        """ Set the protocol for the PSU Control Server."""

        self.device_protocol = PSUProtocol(self, self.psu_index)


class AWGControlServer(AEUControlServer):
    """ AEU Control Server for the AWG."""

    def __init__(self, awg_index: int):
        """ Initialisation of an AEU Control Server for the AWG with the given index.

        Args:
            - awg_index: Index of the AWG (should be 1 or 2).
       """

        self.awg_index = awg_index

        super().__init__("AWG" + str(self.awg_index))

        self.killer = SignalCatcher()

    def set_protocol(self):
        """ Set the protocol for the AWG Control Server."""

        self.device_protocol = AWGProtocol(self, self.awg_index)


@click.group()
def cli():

    pass


@cli.command()
@click.option("--simulator", "--sim", is_flag=True, help="Start the AEU cRIO EGSE Simulator as the backend.")
def start_crio_cs(simulator):
    """ Start the AEU cRIO Control Server.

    To start the AEU cRIO Control Server from the command line (after running setuptools):

        ```bash
            $ aeu_cs start-crio-cs [--sim]
        ```

    Args:
        - simulator: Indicates whether or not to start the Control Server in simulator mode.

    Raises:
        - KeyboardInterrupt: upon keyboard interrupt.
        - SystemExit: upon system exit.
        - Exception: if the control server cannot be started.
    """

    if simulator:

        Settings.set_simulation_mode(True)

    try:

        multiprocessing.current_process().name = "crio_cs"

        crio = CRIOControlServer()
        crio.serve()

    except KeyboardInterrupt:

        print("Shutdown requested...exiting")

    except SystemExit as exit_code:

        print(f"System Exit with code {exit_code}.")
        sys.exit(exit_code)

    except Exception as exc:

        logger.exception(f"An error occurred for the cRIO: {exc}")

    return 0


@cli.command()
@click.option("--simulator", "--sim", is_flag=True, help="Start an AEU PSU EGSE Simulator as the backend.")
@click.argument('index', type=click.IntRange(1, 6))
def start_psu_cs(simulator, index):
    """ Start the AEU PSU Control Server with the given index.

    To start the PSU Control Server from the command line (after running setuptools):

        ```bash
            aeu_cs start-psu-cs INDEX [--sim]
        ```

    Args:
        - simulator: Indicates whether or not to start the Control Server in simulator mode.
        - index: Index of the PSU (should be 1..6).

    Raises:
        - KeyboardInterrupt: upon keyboard interrupt.
        - SystemExit: upon system exit.
        - Exception: if the control server cannot be started.
    """

    if simulator:

        Settings.set_simulation_mode(True)

    try:

        logger.info(f"Starting PSU{index} Control Server")

        multiprocessing.current_process().name = f"psu_cs_{index}"

        psu = PSUControlServer(index)
        psu.serve()

    except KeyboardInterrupt:

        print("Shutdown requested...exiting")

    except SystemExit as exit_code:

        print(f"System Exit with code {exit_code}.")
        sys.exit(exit_code)

    except Exception as exc:

        logger.exception(f"An error occurred for PSU{index}: {exc}")

    return 0


@cli.command()
@click.option("--simulator", "--sim", is_flag=True, help="Start an AEU AWG EGSE Simulator as the backend.")
@click.argument('index', type=click.IntRange(1, 2))
def start_awg_cs(simulator, index):
    """ Start the AEU AWG Control Server with the given index.

    To start the AWG Control Server from the command line (after running setuptools):

        ```bash
            aeu_cs start-awg-cs INDEX [--sim]
        ```

    Args:
        - simulator: Indicates whether or not to start the Control Server in simulator mode.
        - index: Index of the AWG (should be 1 or 2).

    Raises:
        - KeyboardInterrupt: upon keyboard interrupt.
        - SystemExit: upon system exit.
        - Exception: if the control server cannot be started.
    """

    if index == 2:

        try:
            GlobalState.setup.gse.aeu.awg2.calibration
        except AttributeError:
            logger.exception("Starting AWG2 Control Server failed because no setup was loaded " +
                             "or the loaded setup does not contain AWG2 calibration data")

    if simulator:
        Settings.set_simulation_mode(True)

    try:

        logger.info(f"Starting AWG{index} Control Server")

        multiprocessing.current_process().name = f"awg_cs_{index}"

        awg = AWGControlServer(index)
        awg.serve()

    except KeyboardInterrupt:

        print("Shutdown requested...exiting")

    except SystemExit as exit_code:

        print(f"System Exit with code {exit_code}.")
        sys.exit(exit_code)

    except BrokenPipeError as bpe:

        logger.warning(f"BrokenPipeError occurred for AWG{index}: {bpe}")
        logger.info(f"Not reconnecting to AWG{index}")

        # device = awg.device_protocol.awg
        # device.reconnect()

    except Exception as exc:

        logger.exception(f"An error occurred for AWG{index}: {exc}")

    return 0


@cli.command()
def stop_crio_cs():
    """ Shut down the AEU cRIO Control Server.

    To shut down the AEU cRIO Control Server from the command line (after running setuptools):

        ```bash
            aeu_cs stop-crio-cs
        ```
    """

    if is_aeu_cs_active("CRIO"):

        with CRIOProxy() as proxy:

            sp = proxy.get_service_proxy()
            sp.quit_server()


@cli.command()
@click.argument('index', type=click.IntRange(1, 6))
def stop_psu_cs(index: int):
    """ Shut down the AEU PSU Control Server with the given index.

    To shut down the AEU PSU Control Server from the command line (after running setuptools):

        ```bash
            aeu_cs stop-psu-cs INDEX
        ```

    Args:
        - index: Index of the PSU (should be 1..6).
    """

    if is_aeu_cs_active("PSU" + str(index)):

        with PSUProxy(index) as proxy:

            sp = proxy.get_service_proxy()
            sp.quit_server()


@cli.command()
@click.argument('index', type=click.IntRange(1, 2))
def stop_awg_cs(index: int):
    """ Shut down the AEU AWG control server with the given index.

    To shut down the AEU AWG Control Server from the command line (after running setuptools):

        ```bash
            aeu_cs stop-awg-cs INDEX
        ```

    Args:
        - index: Index of the AWG (should be 1 or).
    """

    if is_aeu_cs_active("AWG" + str(index)):

        with AWGProxy(index) as proxy:

            logger.info(f"Shutting down AWG{index} Control Server")

            sp = proxy.get_service_proxy()
            sp.quit_server()


@cli.command()
@click.option("--simulator", "--sim", is_flag=True, help="Start the AEU EGSE Simulators as the backend.")
def start(simulator):
    """ Start the AEU Control Servers.

    To start these from the command line (after running setuptools):

        ```bash
            aeu_cs start [--sim]
        ```

    Args:
        - simulator: Indicates whether or not to start the Control Servers in simulator mode.
    """

    suffix = ""

    if simulator:

        suffix = "--sim"

    logger.info(f"Starting cRIO")

    run(f"aeu_cs start-crio-cs {suffix}", disown=True)

    for index in range(1, 7):

        logger.info(f"Starting PSU{index}")
        run(f"aeu_cs start-psu-cs {index} {suffix}", disown=True)

    for index in range(1, 3):

        logger.info(f"Starting AWG{index}")
        run(f"aeu_cs start-awg-cs {index} {suffix}", disown=True)


@cli.command()
def stop():
    """ Shut down the AEU Control Servers.

    To shut these down from the command line (after running setuptools):

        ```bash
            aeu_cs stop [--sim]
        ```

    Args:
        - simulator: Indicates whether or not to start the Control Servers in simulator mode.
    """

    logger.info(f"Shutting down cRIO")

    run("aeu_cs stop-crio-cs")

    for index in range(1, 7):

        logger.info(f"Shutting down PSU{index}")
        run(f"aeu_cs stop-psu-cs {index}", disown=True)

    for index in range(1, 3):

        logger.info(f"Shutting down AWG{index}")
        run(f"aeu_cs stop-awg-cs {index}", disown=True)


@cli.command()
def status():
    """Print the status of the AEU control servers."""

    # AEU cRIO

    rich.print("AEU cRIO:")

    if is_aeu_cs_active("CRIO"):

        rich.print(f"  Status: [green]active")

        with CRIOProxy() as crio:

            rich.print(f"  Hostname: {crio.get_ip_address()}")
            rich.print(f"  Monitoring port: {crio.get_monitoring_port()}")
            rich.print(f"  Commanding port: {crio.get_commanding_port()}")
            rich.print(f"  Service port: {crio.get_service_port()}")

    else:

        rich.print(f"  Status: [red]not active")

    # PSU

    for psu_index in range(1, 7):

        rich.print(f"AEU PSU{psu_index}:")

        if is_aeu_cs_active(f"PSU{psu_index}"):

            rich.print(f"  Status: [green]active")

            with PSUProxy(psu_index) as psu:

                rich.print(f"  Hostname: {psu.get_ip_address()}")
                rich.print(f"  Monitoring port: {psu.get_monitoring_port()}")
                rich.print(f"  Commanding port: {psu.get_commanding_port()}")
                rich.print(f"  Service port: {psu.get_service_port()}")

        else:

            rich.print(f"  Status: [red]not active")

    # AWG

    for awg_index in [1, 2]:

        rich.print(f"AEU AWG{awg_index}:")

        if is_aeu_cs_active(f"AWG{awg_index}"):

            rich.print(f"  Status: [green]active")

            with AWGProxy(awg_index) as awg:

                rich.print(f"  Hostname: {awg.get_ip_address()}")
                rich.print(f"  Monitoring port: {awg.get_monitoring_port()}")
                rich.print(f"  Commanding port: {awg.get_commanding_port()}")
                rich.print(f"  Service port: {awg.get_service_port()}")

        else:

            rich.print(f"  Status: [red]not active")


if __name__ == "__main__":

    sys.exit(cli())
