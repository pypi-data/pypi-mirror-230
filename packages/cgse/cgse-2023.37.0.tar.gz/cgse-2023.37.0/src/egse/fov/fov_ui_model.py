"""
This module provides the Model (M) in the MVC pattern of the FOV GUI application.
"""

import logging
from math import cos
from math import radians
from math import sin
from math import tan

from egse.coordinates import focal_plane_to_ccd_coordinates
from egse.coordinates import undistorted_to_distorted_focal_plane_coordinates
from egse.hexapod.symetrie.puna_ui import PunaUIModel
from egse.settings import Settings
from egse.setup import get_setup
from egse.stages.huber.smc9300_ui import HuberUIModel

STAGES_SETTINGS = Settings.load("Huber Controller")
FOV_SETTINGS = Settings.load("Field-Of-View")

MODULE_LOGGER = logging.getLogger(__name__)


class FOVUIModel:

    def __init__(self, type_hexapod, type_stages):
        """ Initialisation of models for the Hexapod and the Stages.

        :param type_hexapod: Hexapod implementation to use.  Choices are between:
                             proxy, simulator, and hexapod.

        :param type_stages: Stages implementation to use.  Choices are between:
                            proxy, simulator, and huber.
        """

        self.hexapod_model = PunaUIModel(type_hexapod)
        self.stages_model = HuberUIModel(type_stages)

    ##############
    # Connectivity
    ##############

    def is_connected_hexapod(self):
        """ Checks whether there's a connection with the hexapod.

        :return: True if there's a connection with the hexapod, False otherwise.
        """

        return self.hexapod_model.is_device_connected()

    def is_connected_stages(self):
        """ Checks whether there's a connection with the stages.

        :return: True if there's a connection with the stages, False otherwise.
        """

        return self.stages_model.is_device_connected()

    def reconnect_hexapod(self):
        """ Reconnects to the hexapod."""

        self.hexapod_model.reconnect()

    def reconnect_stages(self):
        """ Reconnects to the stages."""

        self.stages_model.reconnect()

    ###########################################
    # Position of the source on the focal plane
    ###########################################

    def get_position(self):
        """ Calculates the coordinate of the source.

        Calculates the coordinate of the source, given the position of the associated hexapod and stages, and taking
        the field distortion into account.

        :return: Dictionary with the following entries:
                    - "angles": gnomonic distance from the optical axis and in-field angle [degrees]
                    - "pixels": CCD coordinates (row, column) [pixels] and the corresponding CCD code
                    - "mm": focal-plane coordinates (x, y) [mm]
        """

        setup = get_setup()
        offset_phi = setup.gse.stages.calibration.offset_phi
        offset_alpha = setup.gse.stages.calibration.offset_alpha
        alpha_correction_coefficients = setup.gse.stages.calibration.alpha_correction_coefficients

        # Focal-plane coordinates [mm]

        (x, y) = self.get_focal_plane_position()

        # CCD coordinates [pixels]

        (row, column, ccd_code) = focal_plane_to_ccd_coordinates(x, y)

        # Gnomonic distance to optical axis and in-field angle [degrees]

        angle_small_rotation_stage = self.get_rotation_angle_small_rotation_stage()
        theta = (angle_small_rotation_stage + offset_alpha - alpha_correction_coefficients[0]) \
                / alpha_correction_coefficients[1]

        position = {
            "angles": (theta, offset_phi - self.get_rotation_angle_big_rotation_stage()),
            "pixels": (row, column, ccd_code),
            "mm": (x, y)
        }

        return position

    def get_focal_plane_position(self):

        """
        Calculates and returns the focal-plane coordinates (x, y) [mm] of the source, given the
        position of the associated hexapod and stages, and taking the field distortion into account.

        :return: Focal-plane coordinates (x, y) [mm] of the source, given the position of the
                 associated hexapod and stages, and taking the field distortion into account.

        .. todo:: Check whether the light beam goes through the entrance pupil
                  distance_sma / FOV_SETTINGS.HEIGHT_COLLIMATED_BEAM != math.tan(math.radians(angle_small_rotation_stage))
        """

        # Rotation angle of the big rotation stage [degrees]
        # - counterclockwise rotation
        # - 0° -> axis of the focal plane aligned with GL_FIX

        angle_big_rotation_stage = self.get_rotation_angle_big_rotation_stage()

        # Rotation angle of the small rotation stage [degrees]
        # - clockwise rotation
        # - 0° -> ?

        angle_small_rotation_stage = self.get_rotation_angle_small_rotation_stage()

        # Radial distance without field distortion [mm] and corresponding focal-plane coordinates [mm]
        # Note that the height of the lower triangle is very close to the focal length

        theta = 2 * angle_small_rotation_stage # [degrees]

        radial_distance_undistorted = FOV_SETTINGS.FOCAL_LENGTH * tan(radians(theta))

        x_undistorted = -radial_distance_undistorted * cos(-radians(angle_big_rotation_stage))
        y_undistorted = -radial_distance_undistorted * sin(-radians(angle_big_rotation_stage))

        x_distorted, y_distorted = \
            undistorted_to_distorted_focal_plane_coordinates(x_undistorted, y_undistorted,
                                                             FOV_SETTINGS.DISTORTION_COEFFICIENTS,
                                                             FOV_SETTINGS.FOCAL_LENGTH)

        return x_distorted, y_distorted

    def get_focus_position(self):
        """ Returns the focus position (z) [mm]. This is the distance between L6S2 and FPA_SEN.

        :return: Focus position (z) [mm].
        """

        # Distance between FPA_SEN and L6S2 [mm]

        return -self.hexapod_model.get_user_positions()[2]

    def get_rotation_angle_big_rotation_stage(self):
        """ Returns the rotation angle of the big rotation stage [degrees].

        A positive angle corresponds to counterclockwise rotation.

        :return: Rotation angle of the big rotation stage [degrees].

        .. todo:: Where is angle = 0°?
        """

        # Counterclockwise rotation [degrees]

        return self.stages_model.get_current_position(STAGES_SETTINGS.BIG_ROTATION_STAGE)

    def get_rotation_angle_small_rotation_stage(self):
        """ Returns the rotation angle of the small rotation stage [degrees].

        :return: Rotation angle of the small rotation stage [degrees].

        .. todo:: Where is angle = 0°?
        """

        # Counterclockwise rotation [degrees]

        return self.stages_model.get_current_position(STAGES_SETTINGS.SMALL_ROTATION_STAGE)

    def get_distance_translation_stage(self):
        """ Returns the distance between the centre of the scan mirror and the optical axis [mm].

        :return: Distance between the centre of the scan mirror and the optical axis [mm]

        .. todo:: Properly define the zero position.
        """

        # Distance between the optical axis and the SMA [mm]

        return self.stages_model.get_current_position(STAGES_SETTINGS.TRANSLATION_STAGE)
