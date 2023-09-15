import logging
import multiprocessing
import pickle
import threading
import numpy as np

import click
import invoke
import rich
import sys
import zmq
from math import sin, cos, tan, acos, asin, atan, atan2, radians, degrees, pi, sqrt
from numpy import sign
from prometheus_client import start_http_server

from egse.control import is_control_server_active
from egse.fov import store_actual_fov_position
from egse.settings import Settings
from egse.state import GlobalState
from egse.storage import is_storage_manager_active
from egse.storage import register_to_storage_manager
from egse.storage.persistence import CSV
from egse.zmq_ser import connect_address, bind_address

CTRL_SETTINGS = Settings.load("FOV HK Control Server")
LOGGER = logging.getLogger(__name__)
SITE_ID = Settings.load("SITE").ID
ORIGIN = "FOV"

TIMEOUT_RECV = 1.0  # seconds


@click.group()
def cli():
    pass


@cli.command()
def start():
    """ Start the FOV HK Control Server.

    This process will only store the actual FOV position (in field angles, expressed in degrees).  The commanded
    position needs to be stored from the MGSE commanding in plato-test-scripts.

    Under the hood, this method calls the TH-specific implementation.  Only this generic function should be used, not
    the TH-specific implementation.
    """

    multiprocessing.current_process().name = "fov_hk"
    start_http_server(CTRL_SETTINGS.METRICS_PORT)

    # The Storage Manager must be active (otherwise the HK cannot be stored)

    if not is_storage_manager_active():

        LOGGER.error("The Storage Manager is not running, start the core services before running the data acquisition.")
        return

        # Make sure the FOV position HK file contains the following columns:
        #   - timestamp
        #   - FOV_ACT_THETA: the actual gnomonic distance to the optical axis [degrees]
        #   - FOV_ACT_PHI: the actual in-field angle [degrees]
        #   - FOV_CMD_THETA: the commanded gnomonic distance to the optical axis [degrees]
        #   - FOV_CMD_PHI: the commanded in-field angle [degrees]

    register_to_storage_manager(ORIGIN, CSV, prep=dict(mode='a', column_names=["timestamp", "FOV_ACT_THETA",
                                                                               "FOV_ACT_PHI", "FOV_CMD_THETA",
                                                                               "FOV_CMD_PHI"]))

    # Make sure you notice when a command has been issued to stop the FOV HK generation

    context = zmq.Context()

    endpoint = bind_address(CTRL_SETTINGS.PROTOCOL, CTRL_SETTINGS.COMMANDING_PORT)
    commander = context.socket(zmq.REP)
    commander.bind(endpoint)

    poller = zmq.Poller()
    poller.register(commander, zmq.POLLIN)

    # Start listening for HK updates

    sitehash = {
        "CSL": _csl_start,
        "CSL1": _csl1_start,
        "CSL2": _csl2_start,
        "IAS": _ias_start,
        "INTA": _inta_start,
        "SRON": _sron_start,
    }

    sitehash[SITE_ID](commander, poller)


@cli.command()
def start_bg():
    """ Start the generation of FOV position HK as a background process.

    This process will only store the actual FOV position (in field angles, expressed in degrees).  The commanded
    position needs to be stored from the MGSE commanding in plato-test-scripts.

    Under the hood, this method calls the TH-specific implementation.  Only this generic function should be used, not
    the TH-specific implementation.
    """

    invoke.run(f"fov_hk start", disown=True)


class FovHk:

    def __init__(self):

        self.setup = GlobalState.setup
        self.keep_acquiring_fov_hk = True

    def run(self, commander, poller):

        try:

            while True:

                if _check_commander_status(commander, poller):
                    self.keep_acquiring_fov_hk = False
                    break

        except KeyboardInterrupt:

            click.echo("KeyboardInterrupt caught!")
            self.keep_acquiring_fov_hk = False

            # Keyboard interrupt or stop command

        LOGGER.info("Shutting down FOV HK")
        self.close_sockets()
        commander.close(linger=0)

    def start_fov_hk_acquisition(self):

        # Processing the content of the queue should be done in a separate thread

        self.process_fov_hk_thread = threading.Thread(target=self.acquire_fov_hk)
        self.process_fov_hk_thread.daemon = True
        self.process_fov_hk_thread.start()

    def acquire_fov_hk(self):
        pass

    def close_sockets(self):
        pass


class CslFovHk(FovHk):

    def __init__(self):

        super(CslFovHk, self).__init__()

        setup = GlobalState.setup
        self.height_collimated_beam = setup.gse.stages.calibration.height_collimated_beam
        self.offset_delta_x = setup.gse.stages.calibration.offset_delta_x
        self.offset_phi = setup.gse.stages.calibration.offset_phi

        # Create a socket and connect to the monitoring port

        settings = Settings.load("Huber Control Server")
        self.cmd_endpoint = connect_address(settings.PROTOCOL, settings.HOSTNAME, settings.COMMANDING_PORT)

        monitoring_address = connect_address(settings.PROTOCOL, settings.HOSTNAME, settings.MONITORING_PORT)
        self.monitoring_socket = zmq.Context().socket(zmq.SUB)
        self.monitoring_socket.connect(monitoring_address)
        self.monitoring_socket.setsockopt_string(zmq.SUBSCRIBE, "")
        self.monitoring_timeout = 1.0

        self.start_fov_hk_acquisition()

    def acquire_fov_hk(self):

        while self.keep_acquiring_fov_hk:

            try:

                socket_list, _, _ = zmq.select([self.monitoring_socket], [], [], timeout=self.monitoring_timeout)

                # Monitoring information was received (before timeout)

                if self.monitoring_socket in socket_list:

                    pickle_string = self.monitoring_socket.recv()
                    monitoring_info = pickle.loads(pickle_string)

                    # Retrieve the position of the small and the big rotation stage

                    position_big_rotation_stage = monitoring_info["big_rotation_stage_position"]
                    position_translation_stage = monitoring_info["translation_stage_position"]

                    # Gnomonic distance to optical axis and in-field angle [degrees]

                    phi = self.offset_phi - position_big_rotation_stage
                    tan_theta = (self.offset_delta_x - position_translation_stage) / self.height_collimated_beam
                    theta = degrees(atan(tan_theta))

                    store_actual_fov_position(theta, phi)

                elif is_control_server_active(self.cmd_endpoint):
                    self.monitoring_timeout += 0.5

            except zmq.ZMQError:
                pass

    def close_sockets(self):

        self.monitoring_socket.close()


def _csl_start(commander, poller):
    """ Start the generation of FOV position HK for CSL.

    This process will only store the actual FOV position (in field angles, expressed in degrees).  The commanded
    position needs to be stored from the MGSE commanding in plato-test-scripts.

    This function should never be called.  Instead, call the generic function start().

    Args:
        - commander: Commanding socket for the FOV HK generation.
        - poller: Poller for the FOV HK generation.
    """

    csl_fov_hk = CslFovHk()
    csl_fov_hk.run(commander, poller)


class Csl1FovHk(FovHk):

    def __init__(self):

        super(Csl1FovHk, self).__init__()

        setup = GlobalState.setup
        self.offset_alpha = setup.gse.stages.calibration.offset_alpha
        self.alpha_correction_coefficients = setup.gse.stages.calibration.alpha_correction_coefficients
        self.offset_phi = setup.gse.stages.calibration.offset_phi
        self.phi_correction_coefficients = setup.gse.stages.calibration.phi_correction_coefficients

        # Create a socket and connect to the monitoring port

        settings = Settings.load("Huber Control Server")
        self.cmd_endpoint = connect_address(settings.PROTOCOL, settings.HOSTNAME, settings.COMMANDING_PORT)

        monitoring_address = connect_address(settings.PROTOCOL, settings.HOSTNAME, settings.MONITORING_PORT)
        self.monitoring_socket = zmq.Context().socket(zmq.SUB)
        self.monitoring_socket.connect(monitoring_address)
        self.monitoring_socket.setsockopt_string(zmq.SUBSCRIBE, "")
        self.monitoring_timeout = 1.0

        self.start_fov_hk_acquisition()

    def acquire_fov_hk(self):

        while self.keep_acquiring_fov_hk:

            try:

                socket_list, _, _ = zmq.select([self.monitoring_socket], [], [], timeout=self.monitoring_timeout)

                # Monitoring information was received (before timeout)

                if self.monitoring_socket in socket_list:

                    pickle_string = self.monitoring_socket.recv()
                    monitoring_info = pickle.loads(pickle_string)

                    # Retrieve the position of the small and the big rotation stage

                    position_big_rotation_stage = monitoring_info["big_rotation_stage_position"]
                    position_small_rotation_stage = monitoring_info["small_rotation_stage_position"]

                    # Gnomonic distance to optical axis and in-field angle [degrees]

                    theta = (position_small_rotation_stage + self.offset_alpha - self.alpha_correction_coefficients[0])\
                        / self.alpha_correction_coefficients[1]

                    phi_correction = self.phi_correction_coefficients[1] * theta + self.phi_correction_coefficients[0]
                    phi = -position_big_rotation_stage - self.offset_phi - phi_correction

                    store_actual_fov_position(theta, phi)

                elif is_control_server_active(self.cmd_endpoint):
                    self.monitoring_timeout += 0.5

            except zmq.ZMQError:
                pass

    def close_sockets(self):

        self.monitoring_socket.close()


def _csl1_start(commander, poller):
    """ Start the generation of FOV position HK for CSL1.

    This process will only store the actual FOV position (in field angles, expressed in degrees).  The commanded
    position needs to be stored from the MGSE commanding in plato-test-scripts.

    This function should never be called.  Instead, call the generic function start().

    Args:
        - commander: Commanding socket for the FOV HK generation.
        - poller: Poller for the FOV HK generation.
    """

    csl1_fov_hk = Csl1FovHk()
    csl1_fov_hk.run(commander, poller)


def _csl2_start(commander, poller):
    """ Start the generation of FOV position HK for CSL2.

    This process will only store the actual FOV position (in field angles, expressed in degrees).  The commanded
    position needs to be stored from the MGSE commanding in plato-test-scripts.

    This function should never be called.  Instead, call the generic function start().

    Args:
        - commander: Commanding socket for the FOV HK generation.
        - poller: Poller for the FOV HK generation.
    """
    # At this point, the relation between the configuration of the Huber Stages and the source position is considered
    # the same for CSL2 as for CSL1 (only the calibration of the Huber Stages is potentially different in the setup)
    csl2_fov_hk = Csl1FovHk()
    csl2_fov_hk.run(commander, poller)


class SronFovHk(FovHk):

    def __init__(self):

        super(SronFovHk, self).__init__()

        # Create a socket and connect to the monitoring port

        settings = Settings.load("Aerotech Ensemble Control Server")
        self.cmd_endpoint = connect_address(settings.PROTOCOL, settings.HOSTNAME, settings.COMMANDING_PORT)

        monitoring_address = connect_address(settings.PROTOCOL, settings.HOSTNAME, settings.MONITORING_PORT)
        self.monitoring_socket = zmq.Context().socket(zmq.SUB)
        self.monitoring_socket.connect(monitoring_address)
        self.monitoring_socket.setsockopt_string(zmq.SUBSCRIBE, "")
        self.monitoring_timeout = 1.0

        self.start_fov_hk_acquisition()

    def acquire_fov_hk(self):

        while self.keep_acquiring_fov_hk:

            try:

                socket_list, _, _ = zmq.select([self.monitoring_socket], [], [], timeout=self.monitoring_timeout)

                # Monitoring information was received (before timeout)

                if self.monitoring_socket in socket_list:

                    pickle_string = self.monitoring_socket.recv()
                    monitoring_info = pickle.loads(pickle_string)

                    # Update the timeout, to be more in line with the monitoring frequency of the CS (i.e. the delay).
                    # Take 0.5s extra to be on the safe side.

                    monitoring_timeout = monitoring_info["delay"] / 1000.0 + 0.5  # [s]

                    # Retrieve the position of the gimbal

                    rotx = radians(monitoring_info["alpha"])    # [radians]
                    roty = radians(monitoring_info["beta"])     # [radians]

                    tolerance = 1.e-5

                    # Gnomonic distance to optical axis and in-field angle [degrees]

                    theta = degrees(acos(cos(rotx) * cos(roty)))    # [degrees]

                    phi = 0.0
                    if abs(roty) < tolerance:
                        phi = sign(rotx) * pi / 2.
                    elif abs(roty) > tolerance:
                        phi = atan(sign(roty) * tan(rotx) / sin(roty))

                    phi = degrees(phi)      # [degrees]

                    if roty < 0:
                        phi = -180. - phi

                    if phi < -180:
                        phi += 360.

                    store_actual_fov_position(theta, phi)

                elif is_control_server_active(self.cmd_endpoint):
                    self.monitoring_timeout += 0.5

            except zmq.ZMQError:
                pass

    def close_sockets(self):

        self.monitoring_socket.close()


def _sron_start(commander, poller):
    """ Start the generation of FOV position HK for SRON.

    This process will only store the actual FOV position (in field angles, expressed in degrees).  The commanded
    position needs to be stored from the MGSE commanding in plato-test-scripts.

    This function should never be called.  Instead, call the generic function start().

    Args:
        - commander: Commanding socket for the FOV HK generation.
        - poller: Poller for the FOV HK generation.
    """

    sron_fov_hk = SronFovHk()
    sron_fov_hk.run(commander, poller)


class IasFovHk(FovHk):

    def __init__(self):

        super(IasFovHk, self).__init__()

        # Create a socket and connect to the monitoring port

        settings = Settings.load("Hexapod ZONDA Control Server")
        self.cmd_endpoint = connect_address(settings.PROTOCOL, settings.HOSTNAME, settings.COMMANDING_PORT)

        monitoring_address = connect_address(settings.PROTOCOL, settings.HOSTNAME, settings.MONITORING_PORT)
        self.monitoring_socket = zmq.Context().socket(zmq.SUB)
        self.monitoring_socket.connect(monitoring_address)
        self.monitoring_socket.setsockopt_string(zmq.SUBSCRIBE, "")
        self.monitoring_timeout = 1.0

        self.start_fov_hk_acquisition()

    def acquire_fov_hk(self):

        while self.keep_acquiring_fov_hk:

            try:

                socket_list, _, _ = zmq.select([self.monitoring_socket], [], [], timeout=self.monitoring_timeout)

                # Monitoring information was received (before timeout)

                if self.monitoring_socket in socket_list:

                    pickle_string = self.monitoring_socket.recv()
                    monitoring_info = pickle.loads(pickle_string)

                    # Retrieve the rotation angles around the y- and z-axis [degrees]
                    # (the rotation angle around the x-axis and the translation are not needed here)

                    rot_y_z_mini = 1 / 3600  # lower threshold: 1 arcsecond = 1/3600 degree

                    *_, hexapod_rot_y, hexapod_rot_z = monitoring_info["user"]

                    if hexapod_rot_y < rot_y_z_mini and hexapod_rot_z < rot_y_z_mini:
                        theta = 0
                        phi = 0

                    else:
                        hexapod_rot_y = radians(hexapod_rot_y)  # Rotation angle around the x-axis [radians]
                        hexapod_rot_z = radians(hexapod_rot_z)  # Rotation angle around the y-axis [radians]

                        theta = degrees(acos(cos(hexapod_rot_y) * cos(hexapod_rot_z)))
                        phi = degrees(
                            -asin(sin(hexapod_rot_z) / sqrt(1 - pow(cos(hexapod_rot_y) * cos(hexapod_rot_z), 2))))

                    store_actual_fov_position(theta, phi)

                elif is_control_server_active(self.cmd_endpoint):
                    self.monitoring_timeout += 0.5

            except zmq.ZMQError:
                pass

    def close_sockets(self):

        self.monitoring_socket.close()


def _ias_start(commander, poller):
    """ Start the generation of FOV position HK for IAS.

    This process will only store the actual FOV position (in field angles, expressed in degrees).  The commanded
    position needs to be stored from the MGSE commanding in plato-test-scripts.

    This function should never be called.  Instead, call the generic function start().

    Args:
        - commander: Commanding socket for the FOV HK generation.
        - poller: Poller for the FOV HK generation.
    """

    # Calculate the field angles (theta, phi), based on the current configuration of the relevant mechanisms
    # Call store_actual_fov_position to save them to the appropriate HK file

    ias_fov_hk = IasFovHk()
    ias_fov_hk.run(commander, poller)


class IntaFovHk(FovHk):

    def __init__(self):

        super(IntaFovHk, self).__init__()

        # Create a socket and connect to the monitoring port

        settings = Settings.load("Gimbal Control Server")
        self.cmd_endpoint = connect_address(settings.PROTOCOL, settings.HOSTNAME, settings.COMMANDING_PORT)

        monitoring_address = connect_address(settings.PROTOCOL, settings.HOSTNAME, settings.MONITORING_PORT)
        self.monitoring_socket = zmq.Context().socket(zmq.SUB)
        self.monitoring_socket.connect(monitoring_address)
        self.monitoring_socket.setsockopt_string(zmq.SUBSCRIBE, "")
        self.monitoring_timeout = 1.0

        self.start_fov_hk_acquisition()

    def acquire_fov_hk(self):

        while self.keep_acquiring_fov_hk:

            try:

                socket_list, _, _ = zmq.select([self.monitoring_socket], [], [], timeout=self.monitoring_timeout)

                # Monitoring information was received (before timeout)

                if self.monitoring_socket in socket_list:

                    # Retrieve the rotation angles around the y- and z-axis [degrees]
                    # (the rotation angle around the x-axis and the translation are not needed here)

                    pickle_string = self.monitoring_socket.recv()
                    monitoring_info = pickle.loads(pickle_string)

                    # Retrieve the rotation angles around the x- and y-axis [degrees]
                    # See GimbalProtocol.get_status for details
                    grx, gry = monitoring_info["user"]

                    #
                    # According to inta_point_source_to_fov:
                    #   grx = np.rad2deg(-np.arcsin(np.sin(np.deg2rad(theta)) * np.sin(np.deg2rad(phi))))
                    #   gry = np.rad2deg(np.arctan2(np.sin(np.deg2rad(theta)) * np.cos(np.deg2rad(phi)), np.cos(np.deg2rad(theta))))
                    #
                    # grx and gry are already in degrees, therefore:
                    #
                    
                    theta = np.rad2deg(np.arccos(np.cos(np.deg2rad(grx))*np.cos(np.deg2rad(gry))))
                    phi   = np.rad2deg(np.arctan2(-np.sin(np.deg2rad(grx)), np.cos(np.deg2rad(grx))*np.sin(np.deg2rad(gry))))   
                    
                    store_actual_fov_position(theta, phi)

                elif is_control_server_active(self.cmd_endpoint):
                    self.monitoring_timeout += 0.5

            except zmq.ZMQError:
                pass

    def close_sockets(self):
        self.cmd_endpoint.close()
        self.monitoring_socket.close()


def _inta_start(commander, poller):
    """ Start the generation of FOV position HK for INTA.

    This process will only store the actual FOV position (in field angles, expressed in degrees).  The commanded
    position needs to be stored from the MGSE commanding in plato-test-scripts.

    This function should never be called.  Instead, call the generic function start().

    Args:
        - commander: Commanding socket for the FOV HK generation.
        - poller: Poller for the FOV HK generation.
    """

    # Calculate the field angles (theta, phi), based on the current configuration of the relevant mechanisms
    # Call store_actual_fov_position to save them to the appropriate HK file

    inta_fov_hk = IntaFovHk()
    inta_fov_hk.run(commander, poller)


@cli.command()
def stop():
    """Stop the FOV HK Control Server. """

    # In the while True loop in the start command, _should_stop needs to force a break from the loop.When this happens
    # (and also when a keyboard interrupt has been caught), the monitoring socket needs to be closed (this needs to be
    # done in the TH - specific implementation of _start).  Unregistering from the Storage Manager is done
    # automatically.

    response = send_request("quit")
    if response == "ACK":
        rich.print("FOV HK successfully terminated.")
    else:
        rich.print(f"[red] ERROR: {response}")


@cli.command()
def status():
    """Print the status of the FOV HK Control Server."""

    rich.print("FOV HK:")

    response = send_request("status")

    if response.get("status") == "ACK":
        rich.print("  Status: [green]active")
        rich.print(f"  Hostname: {response.get('host')}")
        rich.print(f"  Commanding port: {response.get('command_port')}")
    else:
        rich.print("  Status: [red]not active")


def send_request(command_request: str):
    """Sends a request to the FOV HK Control Server and waits for a response.

    Args:
        - command_request: Request.

    Returns: Response to the request.
    """

    ctx = zmq.Context().instance()
    endpoint = connect_address(CTRL_SETTINGS.PROTOCOL, CTRL_SETTINGS.HOSTNAME, CTRL_SETTINGS.COMMANDING_PORT)
    socket = ctx.socket(zmq.REQ)
    socket.connect(endpoint)

    socket.send(pickle.dumps(command_request))
    rlist, _, _ = zmq.select([socket], [], [], timeout=TIMEOUT_RECV)

    if socket in rlist:
        response = socket.recv()
        response = pickle.loads(response)
    else:
        response = {"error": "Receive from ZeroMQ socket timed out for FOV HK Control Server."}
    socket.close(linger=0)

    return response


def _check_commander_status(commander, poller) -> bool:
    """ Check the status of the commander.

    Checks whether a command has been received by the given commander.

    Returns: True if a quit command was received; False otherwise.

    Args:
        - commander: Commanding socket for the FOV HK generation.
        - poller: Poller for the FOV HK generation.
    """

    socks = dict(poller.poll(timeout=10))   # Timeout of 10ms

    if commander in socks:
        pickle_string = commander.recv()
        command = pickle.loads(pickle_string)

        if command.lower() == "quit":
            commander.send(pickle.dumps("ACK"))
            return True

        if command.lower() == "status":
            response = dict(
                status="ACK",
                host=CTRL_SETTINGS.HOSTNAME,
                command_port=CTRL_SETTINGS.COMMANDING_PORT
            )
            commander.send(pickle.dumps(response))
            return False

    return False


# def handle_command(command) -> dict:
#     """Handle commands that are sent to the commanding socket."""
#
#     response = dict(
#         timestamp=format_datetime(),
#     )
#
#     if command.lower() == 'status':
#         response.update(dict(status="ACK",
#                              host=CTRL_SETTINGS.HOSTNAME,
#                              listening_port=,
#                              command_port=CTRL_SETTINGS.COMMANDING_PORT
#                              ))
#
#     return response


if __name__ == "__main__":

    sys.exit(cli())
