"""
This module provides the Controller (C) in the MVC pattern that makes up the FOV GUI application.
"""

import logging

from PyQt5.QtCore import QTimer

from egse.observer import Observer
from egse.settings import Settings

STAGES_SETTINGS = Settings.load("Huber Controller")

MODULE_LOGGER = logging.getLogger(__name__)


class FOVUIController(Observer):

    def __init__(self, model, view):

        """ Initialisation of the Controller in the MVC pattern that makes up the FOV GUI application.

        :param model: Model in the MVC pattern that makes up the FOV GUI application.

        :param view: View in the MVC pattern that makes up the FOV GUI application.
        """

        # MVC + Observer pattern

        self.model = model
        self.view = view
        self.view.addObserver(self)

        self.create_timer()

        # Hexapod connected?

        if self.model.is_connected_hexapod():

            self.view.set_connection_state_hexapod("connected")
            self.hexapod_connected = True

        else:

            self.view.set_connection_state_hexapod("disconnected")
            self.stop_timer()
            self.hexapod_connected = False

        # Stages connected?

        if self.model.is_connected_stages():

            self.view.set_connection_state_stages("connected")
            self.stages_connected = True

        else:

            self.view.set_connection_state_stages("disconnected")
            self.stop_timer()
            self.stages_connected = False

        # Hexapod ánd Stages connected

        if self.model.is_connected_hexapod() and self.model.is_connected_stages():

            self.start_timer()

    def create_timer(self):
        """ Create a timer that will update the states every second."""

        self.states_capture_timer = QTimer()

        # This is only needed when the Timer needs to run in another Thread
        # self.states_capture_timer.moveToThread(self)

        self.states_capture_timer.timeout.connect(self.update_values)
        self.states_capture_timer.setInterval(200)

    def start_timer(self):
        """ Start timer."""

        self.states_capture_timer.start()

    def stop_timer(self):
        """ Stop timer."""

        self.states_capture_timer.stop()

    def update_values(self):
        """ Update the position of the mechanisms and the source.

        Fetch the position of the mechanisms from the model and update the GUI: the positions of the mechanisms need to
        be updated, as well as the position of the source on the FOV.  The position of a mechanism can only be fetched
        (and updated in the GUI) if there's a connection with the control server.

        .. todo:: We need to know the focus position and not the position of the hexapod w.r.t.
                  the homing position.
        """

        if not self.model.is_connected_hexapod():

            MODULE_LOGGER.debug("Not connected to the hexapod control server")
            self.view.set_connection_state_hexapod("disconnected")

        elif not self.model.is_connected_stages():

            MODULE_LOGGER.debug("Not connected to the stages control server")
            self.view.set_connection_state_stages("disconnected")

        else:

            self.view.set_connection_state_hexapod("connected")
            self.view.set_connection_state_stages("connected")

            # Update position of the mechanisms
            #   - SMA: distance from the optical axis + orientation of the scan mirror
            #   - big rotation stage -> orientation
            #   - hexapod -> focus position

            self.view.update_sma(self.model.get_distance_translation_stage(),
                                 self.model.get_rotation_angle_small_rotation_stage())
            self.view.update_big_rotation_stage(self.model.get_rotation_angle_big_rotation_stage())
            self.view.update_focus_position(self.model.get_focus_position())

            # Focal-plane coordinates (x,y) [mm]

            position = self.model.get_position()
            self.view.update_source_position(position)

        return

    def update(self, changed_object):

        return

    def do(self, actions):

        for action, value in actions.items():
            MODULE_LOGGER.debug(f"do {action} with {value}")
            print(f"do {action} with {value}")
