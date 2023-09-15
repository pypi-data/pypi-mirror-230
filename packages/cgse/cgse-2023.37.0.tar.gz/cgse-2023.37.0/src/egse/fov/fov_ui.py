import pickle
from pathlib import Path

import sys
import zmq
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QThread, QLockFile
from PyQt5.QtGui import QCloseEvent, QFont, QIcon
from PyQt5.QtWidgets import QMainWindow, QLabel, QFrame, QHBoxLayout, QGridLayout, QVBoxLayout, QApplication, QAction, \
    QWidget, QSizePolicy, QMessageBox
from math import tan, radians

from egse import coordinates
from egse.config import find_file
from egse.control import is_control_server_active
from egse.coordinates import focal_plane_to_ccd_coordinates
from egse.gui import VLine
from egse.gui.focalplane import FocalPlaneWidgetWithSourcePosition
from egse.gui.mechanisms import ScanMirrorAssemblyWidget, BigRotationStageWidget, FocusPositionWidget
from egse.help.help_ui import HelpWindow, HELP_TOPICS
from egse.observer import Observer, Observable
from egse.resource import get_resource
from egse.settings import Settings
from egse.state import GlobalState
from egse.zmq_ser import connect_address

FONT = QFont("Helvetica", 18)

STAGES_SETTINGS = Settings.load("Huber Control Server")
HEXAPOD_SETTINGS = Settings.load("Hexapod PUNA Control Server")


class MonitoringWorker(QObject):

    def __init__(self, settings):
        """ Initialisation of a monitoring worker.

        This monitoring worker will listen on the monitoring port of the Control Server, based on the given settings.

        Args:
            - settings: Settings with the connection information (which was loaded from the settings file).
        """

        super(MonitoringWorker, self).__init__()

        self.active = False

        self.monitoring_socket = None
        self.monitoring_timeout = 0.5  # [s]
        self.commanding_address = None
        self.is_socket_connected = False

        self.connect_socket(settings)

    def connect_socket(self, settings):
        """ Create a socket and connect to the monitoring port.

        Args:
            - settings: Settings with the connection information (which was loaded from the settings file).
        """

        try:

            # Ctrl settings:
            #   - transport protocol
            #   - hostname
            #   - commanding port (to check whether the CS is active)
            #   - monitoring port (to ask for process information)

            transport = settings.PROTOCOL
            hostname = settings.HOSTNAME
            commanding_port = settings.COMMANDING_PORT
            monitoring_port = settings.MONITORING_PORT

            # Create a socket and connect to the monitoring port

            monitoring_address = connect_address(transport, hostname, monitoring_port)
            self.monitoring_socket = zmq.Context().socket(zmq.SUB)
            self.monitoring_socket.connect(monitoring_address)
            self.monitoring_socket.setsockopt_string(zmq.SUBSCRIBE, "")

            # Address of the commanding port
            # This is needed when checking whether or not the CS is active

            self.commanding_address = connect_address(transport, hostname, commanding_port)

            self.is_socket_connected = True

        except AttributeError:

            self.is_socket_connected = False

    def stop(self):
        """ Stop the monitoring worker.

        The monitoring socket is disconnected from the monitoring port and is then closed immediately.
        """

        self.is_socket_connected = False
        self.monitoring_socket.close()

        # self.monitoring_socket.disconnect(self.monitoring_address)
        # self.monitoring_socket.close(linger=0)

    def start_process(self):
        """ Start listening on the monitoring port.

        If the Control Server is not active when the thread starts listening on the monitoring port, a signal is emitted
        to notify the GUI.
        """

        self.run()

    # @pyqtSlot()
    def run(self):

        raise NotImplementedError


class StagesMonitoringWorker(MonitoringWorker):
    """ Worker for monitoring the position of the stages."""

    # The worker will send a signal with three floats and one dictionaries:
    # The floats will be:
    #   - Commanded position of the big rotation stage [degrees]
    #   - Commanded position of the small rotation stage [degrees]
    #   - Commanded position of the translation stage [mm]
    # The dictionary will have the following entries:
    #   - "angles": Tuple with the field angles (theta, phi) [degrees]
    #   - "pixels": Tuple with the CCD coordinates (row, column) [pixels] and the CCD code
    #   - "mm": Tuple with the focal-plane coordinates (x, y) [pixels]

    stages_position_signal = pyqtSignal(float, float, float, dict)

    def __init__(self):
        """ Initialisation of a monitoring worker for the stages.

        This monitoring worker will listen on the monitoring port of the Huber Control Server.
        """

        super(StagesMonitoringWorker, self).__init__(STAGES_SETTINGS)

        # When new monitoring information comes in, these variables will contain the previous values for the position
        # of the stages (as currently displayed in the GUI).  Once we have checked whether changes have occurred since
        # the last time monitoring information was received, these values will be overwritten by the new ones.

        self.position_big_rotation_stage = None
        self.position_small_rotation_stage = None
        self.position_translation_stage = None

        # Information from the setup

        setup = GlobalState.setup

        self.focal_length = setup.camera.fov.focal_length_mm
        self.offset_alpha = setup.gse.stages.calibration.offset_alpha
        self.offset_phi = setup.gse.stages.calibration.offset_phi
        self.offset_delta_x = setup.gse.stages.calibration.offset_delta_x
        self.alpha_correction_coefficients = setup.gse.stages.calibration.alpha_correction_coefficients
        self.phi_correction_coefficients = setup.gse.stages.calibration.phi_correction_coefficients

        self.distortion_coefficients = setup.camera.fov.distortion_coefficients
        self.height_collimated_beam = setup.gse.stages.calibration.height_collimated_beam



    @pyqtSlot()
    def run(self):
        """ Keep on listening on the monitoring port of the stages.

        If monitoring information is received before the timeout, a signal with the monitoring information is emitted.
        Otherwise, it is checked whether or not the Control Server is active.  If not, a signal is emitted with the
        process name.  Otherwise, the timeout for monitoring was too strict (and it will therefore be increased by
        0.5s).
        """

        self.active = True

        while self.is_socket_connected and self.active:

            try:

                socket_list, _, _ = zmq.select([self.monitoring_socket], [], [], timeout=self.monitoring_timeout)

                # Monitoring information was received (before timeout)

                if self.monitoring_socket in socket_list:

                    pickle_string = self.monitoring_socket.recv()
                    monitoring_info = pickle.loads(pickle_string)

                    # Update the timeout, to be more in line with the monitoring frequency of the CS (i.e. the delay).
                    # Take 0.5s extra to be on the safe side.

                    self.monitoring_timeout = monitoring_info["delay"] / 1000.0 + 0.5    # [s]

                    if self.position_has_changed(monitoring_info):

                        self.stages_position_signal.emit(self.position_big_rotation_stage,
                                                         self.position_small_rotation_stage,
                                                         self.position_translation_stage,
                                                         self.get_position())

            except zmq.ZMQError:

                pass

            # Timeout occurred

            else:

                # The CS is not active

                if not is_control_server_active(self.commanding_address):

                    # TODO
                    pass

                # The CS is active, but the timeout was too strict

                else:

                    self.monitoring_timeout += 0.5

    def position_has_changed(self, monitoring_info: dict):
        """ Check whether the position of at least one of the stages has changed.

        Check whether the position of at least one of the changes has changed since the previous time monitoring
        information was received.

        If the position of the stages has changed, the previous values are updated.

        Args:
            - monitoring_info: Monitoring information for the stages.

        Returns: True if the position of at least one of the stages has changed; False otherwise.
        """

        position_has_changed = False

        # Big rotation stage

        position_big_rotation_stage = monitoring_info["big_rotation_stage_position"]

        if position_big_rotation_stage != self.position_big_rotation_stage:

            self.position_big_rotation_stage = position_big_rotation_stage
            position_has_changed = True

        # Small rotation stage

        position_small_rotation_stage = monitoring_info["small_rotation_stage_position"]

        if position_small_rotation_stage != self.position_small_rotation_stage:

            self.position_small_rotation_stage = position_small_rotation_stage
            position_has_changed = True

        # Translation stage

        position_translation_stage = monitoring_info["translation_stage_position"]

        if position_translation_stage != self.position_translation_stage:

            self.position_translation_stage = position_translation_stage
            position_has_changed = True

        return position_has_changed

    def get_position(self):
        """ Calculates the coordinate of the source.

        Calculates the coordinate of the source, given the position of the associated hexapod and stages, and taking
        the field distortion into account.

        :return: Dictionary with the following entries:
                    - "angles": gnomonic distance from the optical axis and in-field angle [degrees]
                    - "pixels": CCD coordinates (row, column) [pixels] and the corresponding CCD code
                    - "mm": focal-plane coordinates (x, y) [mm]
        """

        # TODO Check whether the light beam passes through the entrance pupil

        # Gnomonic distance to optical axis and in-field angle [degrees]

        theta = (self.position_small_rotation_stage + self.offset_alpha - self.alpha_correction_coefficients[0]) \
            / self.alpha_correction_coefficients[1]

        phi_correction = self.phi_correction_coefficients[1] * theta + self.phi_correction_coefficients[0]
        phi = -self.position_big_rotation_stage - self.offset_phi - phi_correction

        # Focal-plane coordinates [mm]

        x, y = coordinates.angles_to_focal_plane_coordinates(theta, phi)

        # CCD coordinates [pixels]

        (row, column, ccd_code) = focal_plane_to_ccd_coordinates(x, y)

        position = {
            "angles": (theta, phi),
            "pixels": (row, column, ccd_code),
            "mm": (x, y)
        }

        return position

    def light_beam_through_entrance_pupil(self):
        """ Check whether the light beam goes through the entrance pupil.

        Returns: True of the light beam passes through the entrance pupil; False otherwise.
        """

        distance_sma = -self.position_translation_stage + self.offset_delta_x

        return distance_sma / self.height_collimated_beam == \
            tan(radians(self.position_small_rotation_stage + self.offset_alpha + 45))

    # def get_focal_plane_position(self):
    #
    #     """
    #     Calculates and returns the focal-plane coordinates (x, y) [mm] of the source, given the
    #     position of the associated hexapod and stages, and taking the field distortion into account.
    #
    #     :return: Focal-plane coordinates (x, y) [mm] of the source, given the position of the
    #              associated hexapod and stages, and taking the field distortion into account.
    #     """
    #
    #     angle_big_rotation_stage = self.position_big_rotation_stage

        # # Rotation angle of the big rotation stage [degrees]
        # # - counterclockwise rotation
        # # - 0° -> axis of the focal plane aligned with GL_FIX
        #
        # angle_big_rotation_stage = self.position_big_rotation_stage
        #
        # # Rotation angle of the small rotation stage [degrees]
        # # - clockwise rotation
        # # - 0° -> ?
        #
        # angle_small_rotation_stage = self.position_small_rotation_stage
        #
        # # Radial distance without field distortion [mm] and corresponding focal-plane coordinates [mm]
        # # Note that the height of the lower triangle is very close to the focal length
        #
        # theta = 2 * angle_small_rotation_stage  # [degrees]
        #
        # radial_distance_undistorted = self.focal_length * tan(radians(theta))
        #
        # x_undistorted = -radial_distance_undistorted * cos(-radians(angle_big_rotation_stage))
        # y_undistorted = -radial_distance_undistorted * sin(-radians(angle_big_rotation_stage))
        #
        # x_distorted, y_distorted = \
        #     undistorted_to_distorted_focal_plane_coordinates(x_undistorted, y_undistorted,
        #                                                      self.distortion_coefficients, self.focal_length)
        #
        # return x_distorted, y_distorted


class HexapodMonitoringWorker(MonitoringWorker):
    """ Worker for monitoring the position of the hexapod."""

    # The worker will send a signal with the following information:
    #   - focus positions [mm]

    hexapod_position_signal = pyqtSignal(float)

    def __init__(self):
        """ Initialisation of a monitoring worker for the hexapod.

        This monitoring worker will listen on the monitoring port of the Hexapod PUNA Control Server.
        """

        super(HexapodMonitoringWorker, self).__init__(HEXAPOD_SETTINGS)

        self.focus_position = None

    @pyqtSlot()
    def run(self):
        """ Keep on listening on the monitoring port of the hexapod.

        If monitoring information is received before the timeout, a signal with the monitoring information is emitted.
        Otherwise, it is checked whether or not the Control Server is active.  If not, a signal is emitted with the
        process name.  Otherwise, the timeout for monitoring was too strict (and it will therefore be increased by
        0.5s).
        """
        self.active = True

        while self.is_socket_connected and self.active:

            try:

                socket_list, _, _ = zmq.select([self.monitoring_socket], [], [], timeout=self.monitoring_timeout)

                # Monitoring information was received (before timeout)

                if self.monitoring_socket in socket_list:

                    pickle_string = self.monitoring_socket.recv()
                    monitoring_info = pickle.loads(pickle_string)

                    # Update the timeout, to be more in line with the monitoring frequency of the CS (i.e. the delay).
                    # Take 0.5s extra to be on the safe side.

                    self.monitoring_timeout = monitoring_info["delay"] / 1000.0 + 0.5    # [s]

                    if self.position_has_changed(monitoring_info):
                        self.hexapod_position_signal.emit(self.focus_position)

            except zmq.ZMQError:

                pass

            # Timeout occurred

            else:

                # The CS is not active

                if not is_control_server_active(self.commanding_address):

                    pass

                # The CS is active, but the timeout was too strict

                else:

                    self.monitoring_timeout += 0.5

    @staticmethod
    def get_focus_position(monitoring_info: dict):

        return -monitoring_info["user"][2]

    def position_has_changed(self, monitoring_info: dict):
        """ Check whether the focus position has changed.

        Check whether the focus position has changed since the previous time monitoring information was received.

        If the focus position has changed, the previous value is updated.

        Args:
            - monitoring_info: Monitoring information for the hexapod.

        Returns: True if the focus position has changed; False otherwise.
        """

        focus_position = self.get_focus_position(monitoring_info)

        if focus_position != self.focus_position:

            self.focus_position = focus_position
            return True

        return False


class FOVUIView(QMainWindow, Observable):

    def __init__(self):

        """
        Open a window and initialiase the GUI.  The GUI is divided into two parts.  On the
        left there are three widgets, showing the current setting of the stages and the focus
        position.  On the right the focal plane is shown, together with a blue circle indicating
        the size of the field-of-view, and a red dot indicating the current position of the source.
        """

        super().__init__()

        self.setGeometry(300, 300, 1500, 1000)
        self.setWindowTitle("FOV Position GUI")

        setup = GlobalState.setup
        self.fov_radius_mm = setup.camera.fov.radius_mm

        # Monitoring the stages

        self.stages_monitoring_thread = QThread(self)
        self.stages_monitoring_worker = StagesMonitoringWorker()
        self.stages_monitoring_worker.moveToThread(self.stages_monitoring_thread)

        self.stages_monitoring_worker.stages_position_signal.connect(self.on_stages_position_change_signal)
        self.stages_monitoring_thread.started.connect(self.stages_monitoring_worker.start_process)
        self.stages_monitoring_thread.start()

        # Monitoring the hexapod

        self.hexapod_monitoring_thread = QThread(self)
        self.hexapod_monitoring_worker = HexapodMonitoringWorker()
        self.hexapod_monitoring_worker.moveToThread(self.hexapod_monitoring_thread)

        self.hexapod_monitoring_worker.hexapod_position_signal.connect(self.on_hexapod_position_change_signal)
        self.hexapod_monitoring_thread.started.connect(self.hexapod_monitoring_worker.start_process)
        self.hexapod_monitoring_thread.start()

        # Build up the GUI

        self.source_position_text = QLabel()        # "Current source position"
        self.source_position_angles_text = QLabel()  # (theta, phi)
        self.source_position_pixels_text = QLabel()  # (row, column)
        self.source_position_mm_text = QLabel()  # (xFP, yFP)

        self.sma = ScanMirrorAssemblyWidget()
        self.big_rotation_stage = BigRotationStageWidget()
        self.focus_position = FocusPositionWidget()
        self.focal_plane = FocalPlaneWidgetWithSourcePosition()

        self.init_ui()

    def init_ui(self):
        """ Initialisation of the GUI.

        The GUI is divided into two parts.  On the left there are three widgets, showing the current setting of the
        stages and the focus position. On the right the focal plane is shown, together with a blue circle indicating the
        size of the field-of-view, and a red dot indicating the current position of the source.
        """

        app_frame = QFrame()
        app_frame.setObjectName("AppFrame")

        hbox = QHBoxLayout()

        self.create_toolbar()
        self.create_statusbar()

        # Mechanisms

        mechanisms_frame = QFrame()
        mechanisms_frame.setObjectName("Mechanisms")

        vbox_left = QGridLayout()
        vbox_left.addWidget(self.sma)
        vbox_left.addWidget(self.big_rotation_stage)
        vbox_left.addWidget(self.focus_position)

        mechanisms_frame.setLayout(vbox_left)

        # FOV

        fpa_frame = QFrame()
        fpa_frame.setObjectName("FOV")

        vbox_right = QVBoxLayout()
        vbox_right.addWidget(self.focal_plane)

        # Current source position

        self.source_position_text.setFont(FONT)
        vbox_right.addWidget(self.source_position_text)

        self.source_position_angles_text.setIndent(50)
        self.source_position_angles_text.setFont(FONT)
        self.source_position_angles_text.setStatusTip(
            "Gnomonic distance to the optical axis " + u"\u03B8 and in-field angle " + u"\u03C6")
        vbox_right.addWidget(self.source_position_angles_text)

        self.source_position_pixels_text.setIndent(50)
        self.source_position_pixels_text.setFont(FONT)
        self.source_position_pixels_text.setStatusTip("Pixel coordinates on specified CCD")
        vbox_right.addWidget(self.source_position_pixels_text)

        self.source_position_mm_text.setIndent(50)
        self.source_position_mm_text.setFont(FONT)
        self.source_position_mm_text.setStatusTip("Focal-plane coordinates")
        vbox_right.addWidget(self.source_position_mm_text)

        fpa_frame.setLayout(vbox_right)

        # Putting everything in place

        hbox.addWidget(mechanisms_frame)
        hbox.addWidget(fpa_frame)

        app_frame.setLayout(hbox)

        self.setCentralWidget(app_frame)

    def create_toolbar(self):

        # # The Home action is used to command the Homing to the Hexapod.
        #
        # self.homing = TouchButton(
        #     name="HOMING",
        #     status_tip="perform a homing operation (ON ALL THE STAGES)",
        #     selected=get_resource(":/icons/home.svg"),
        #     disabled=get_resource(":/icons/home-disabled.svg"),
        # )
        # self.homing.clicked.connect(self.onClick)
        #
        # # The Clear action is used to command the ClearErrors to the Hexapod.
        #
        # self.clear_errors = TouchButton(
        #     name="CLEAR-ERRORS",
        #     status_tip="clear the error list on the controller (FOR ALL STAGES)",
        #     selected=get_resource(":/icons/erase.svg"),
        #     disabled=get_resource(":/icons/erase-disabled.svg"),
        # )
        # self.clear_errors.clicked.connect(self.onClick)
        #
        # # The Reconnect action is used to reconnect to the control server
        #
        # self.cs_connection = ToggleButton(
        #     name="CS-CONNECT",
        #     status_tip="connect-disconnect huber stages control server.",
        #     selected=get_resource(":/icons/cs-connected.svg"),
        #     not_selected=get_resource(":/icons/cs-not-connected.svg"),
        #     disabled=get_resource(":/icons/cs-connected-disabled.svg")
        # )
        # self.cs_connection.clicked.connect(self.onClick)
        #
        # # The Reconnect action is used to reconnect the device
        #
        # self.device_connection = ToggleButton(
        #     name="DEVICE-CONNECT",
        #     status_tip="connect-disconnect the huber stages controller",
        #     selected=get_resource(":/icons/plugged.svg"),
        #     not_selected=get_resource(":/icons/unplugged.svg"),
        #     disabled=get_resource(":/icons/plugged-disabled.svg")
        # )
        # self.device_connection.clicked.connect(self.onClick)
        #
        # # The STOP button is used to immediately stop the current motion
        #
        # stop_button = QIcon(str(get_resource(":/icons/stop.svg")))
        #
        # self.stop_action = QAction(stop_button, "STOP", self)
        # self.stop_action.setToolTip("STOP Movement")
        # self.stop_action.triggered.connect(self.onClick)

        # The HELP button is used to show the on-line help in a browser window

        help_button = QIcon(str(get_resource(":/icons/info.svg")))

        self.help_action = QAction(help_button, "INFO", self)
        self.help_action.setToolTip("Browse the on-line documentation")
        self.help_action.triggered.connect(self.on_click)

        # spacer widget to help with aligning STOP button to the right

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.toolbar = self.addToolBar("MainToolbar")
        # self.toolbar.addWidget(self.homing)
        # self.toolbar.addWidget(self.clear_errors)
        # self.toolbar.addWidget(self.device_connection)
        # self.toolbar.addWidget(self.cs_connection)
        self.toolbar.addWidget(spacer)
        # self.toolbar.addAction(self.stop_action)
        self.toolbar.addAction(self.help_action)

        return self.toolbar

    def create_statusbar(self):
        """ Create a status bar.

        Returns: Status bar.
        """

        self.statusBar().setStyleSheet("border: 0; background-color: #FFF8DC;")
        self.statusBar().setStyleSheet("QStatusBar::item {border: none;}")
        self.statusBar().addPermanentWidget(VLine())
        # self.statusBar().addPermanentWidget(self.mode_label)

    def on_click(self):

        sender = self.sender()
        self.notifyObservers(sender)

    def on_stages_position_change_signal(self, position_big_rotation_stage: float, position_small_rotation_stage: float,
                                         position_translation_stage: float, source_position: dict):
        """ Update the GUI for changes in the position of the stages.

        Args:
            - position_big_rotation_stage: Rotation angle for the new configuration of the big rotation stage [degrees].
                                           This does not include the offset!
            - position_small_rotation_stage: Orientation angle of the scan mirror [degrees].  This does not include the
                                             offset!
            - position_translation_stage: Distance between the scan mirror and the optical axis (along the translation
                                          stage) for the new configuration of the scan mirror assembly [mm].  This does
                                          not include the offset!
            - source_position: Dictionary with the following entries:
                    - "angles": tuple with the field angles (theta, phi) [degrees];
                    - "pixels": tuple with the pixel coordinates (row, column) [pixels] and CCD code;
                    - "mm": tuple with the focal-plane coordinates (x, y) [mm].
        """

        # Mechanisms

        self.update_sma(position_translation_stage, position_small_rotation_stage)
        self.update_big_rotation_stage(position_big_rotation_stage)

        # Source position

        self.update_source_position(source_position)

    def on_hexapod_position_change_signal(self, focus_position: float):
        """ Update the GUI for changes in the position of the hexapod."""

        self.update_focus_position(focus_position)

    def update_sma(self, distance, angle):
        """ Update the shown configuration of the scan mirror assembly.

        The orientation of the scan mirror must be changed, and the labels showing the distance from the scan
        mirror to the optical axis (along the translation stage) and the orientation angle of the scan mirror must be
        updated.

        Args
            - distance: Distance between the scan mirror and the optical axis (along the translation stage) for the new
                        configuration of the scan mirror assembly [mm].  This does not include the offset!
            - angle: Orientation angle of the scan mirror [degrees].  This does not include the offset!
        """

        self.sma.update_plot(distance, angle)

    def update_big_rotation_stage(self, angle):
        """ Update the shown configuration of the big rotation stage.

        The orientation of GL_ROT w.r.t. GL_FIX must be set to the given angle.

        Args:
            - angle: Rotation angle for the new configuration of the big rotation stage [degrees].  This does not
                     include the offset!
        """

        self.big_rotation_stage.update(angle)

    def update_focus_position(self, focus_position):
        """ Update the shown focus position.

        Args:
            - focus_position: New focus position [mm].
        """

        self.focus_position.update_plot(focus_position)

    def update_source_position(self, position: dict):
        """ Update the position of the source in the focal plane to the given position.

        The red dot must move on the focal plane (movement may not be visible) and the text label with the focal-plane
        coordinates must be updated.

        Args:
            - position: Dictionary with the following entries:

                - "angles": tuple with the field angles (theta, phi) [degrees];
                - "pixels": tuple with the pixel coordinates (row, column) [pixels] and CCD code;
                - "mm": tuple with the focal-plane coordinates (x, y) [mm].
        """

        (theta, phi) = position["angles"]
        (row, column, ccd_code) = position["pixels"]
        (x_fp, y_fp) = position["mm"]

        # Update the red dot in the plot

        self.focal_plane.update_source_position(x_fp, y_fp)

        # Update the text label

        if abs(x_fp) > self.fov_radius_mm or abs(y_fp) > self.fov_radius_mm:

            # MODULE_LOGGER.debug("Current source position: outside FOV")

            self.source_position_text.setText("Current source position: outside FOV")
            self.source_position_angles_text.setText("")
            self.source_position_pixels_text.setText("")
            self.source_position_mm_text.setText("")

        else:

            self.source_position_text.setText("Current source position:")
            self.source_position_angles_text.setText(
                u"\u2022" + "(" + u"\u03B8" + ", " + u"\u03C6" + ") [" + u"\u00B0" + "] = ({:.2f}, {:.2f})"
                .format(theta, phi))

            if ccd_code is None:

                self.source_position_pixels_text.setText(u"\u2022" + " source doesn't fall on any CCD")

            else:

                self.source_position_pixels_text.setText(
                    u"\u2022" + "(x<sub>CCD</sub>, y<sub>CCD</sub>) [pixels] = ({:.2f}, {:.2f}) on CCD "
                    .format(column, row) + str(ccd_code))

            self.source_position_mm_text.setText(
                u"\u2022" + "(x<sub>FP</sub>, y<sub>FP</sub>) [mm] = ({:.2f}, {:.2f})".format(x_fp, y_fp))

    def closeEvent(self, close_event: QCloseEvent) -> None:
        """ Make sure that all threads are stopped when the GUI is closed.

        Args:
            - close_event: Close event received when the GUI is closed.
        """

        # Stages

        self.stages_monitoring_worker.active = False
        self.stages_monitoring_thread.quit()
        self.stages_monitoring_thread.wait()

        # Hexapod

        self.hexapod_monitoring_worker.active = False
        self.hexapod_monitoring_thread.quit()
        self.hexapod_monitoring_thread.wait()


class FOVUIController(Observer):

    def __init__(self, view):

        self.view = view
        self.view.addObserver(self)

        self.help_window = HelpWindow(topic_url=HELP_TOPICS["smc9300_ui"])

    def update(self, changed_object):

        text = changed_object.text()

        if text == "INFO":

            self.help_window.show()

    def do(self, actions):

        pass


def main():
    lock_file = QLockFile(str(Path("~/fov_ui.app.lock").expanduser()))

    styles_location = find_file("styles.qss", in_dir="egse/gui")

    args = list(sys.argv)
    args[1:1] = ['-stylesheet', str(styles_location)]

    app = QApplication(args)
    app.setWindowIcon(QIcon(str(get_resource(":/icons/location-marker.svg"))))

    if lock_file.tryLock(100):
        view = FOVUIView()
        FOVUIController(view)
        view.show()

        return app.exec_()
    else:
        error_message = QMessageBox()
        error_message.setIcon(QMessageBox.Warning)
        error_message.setWindowTitle("Error")
        error_message.setText("The FOV GUI application is already running!")
        error_message.setStandardButtons(QMessageBox.Ok)

        return error_message.exec()


if __name__ == "__main__":
    sys.exit(main())
