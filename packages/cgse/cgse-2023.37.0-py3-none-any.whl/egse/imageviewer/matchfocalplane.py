"""
This module provides a (local) plugin for the Ginga reference viewer, rotating the
sub-field to match the orientation of the focal plane.  The orientation angle of the
sub-field (and CCD) w.r.t. the focal plane (in degrees) is read from the "CROTA2" 
keyword in the header of the loaded FITS file.

To start the Ginga reference viewer, with this extra plugin, execute the following set of commands:

    $ mkdir $HOME/.ginga/plugins
    $ cp matchfocalplane.py $HOME/.ginga/plugins/MatchFocalPlane.py
    $ ginga --plugins=MatchFocalPlane --loglevel=20 --stderr --log=/tmp/ginga.log

The plugin will then be available via the "Operation" button in the Plugin Manager bar
(currently under "Custom").

Alternatively, you can start the image viewer with the command:

    $ ./bin/start-image-viewer.bash

This is the same as the Ginga reference viewer, with all the additional PLATO-specific
plugins.  These plugins will then be available via the "Operation" button in the Plugin Manager bar
(under "PLATO").
"""

from ginga import GingaPlugin
from egse.gui.focalplane import FocalPlaneWidgetWithSubField
from ginga.gw import Widgets

class MatchFocalPlane(GingaPlugin.LocalPlugin):

    def __init__(self, fv, fitsimage):

        """
        Initialisation of a new (local) plugin for the Ginga reference viewer, to rotate 
        the sub-field to match the orientation of the focal plane.  The orientation angle
        of the sub-field (and CCD) w.r.t. the focal plane (in degrees) is read from the
        "CROTA2" keyword in the header of the loaded FITS file.
        Called when the plugin is loaded from the first time.

        :param fv: Reference to the Ginga (reference viewer) shell.

        :param fitsimage: Reference to the specific viewer object associated with
                          the channel on which the plugin is being invoked.
        """

        super(MatchFocalPlane, self).__init__(fv, fitsimage)

        self.t_ = self.fitsimage.get_settings()

    def build_gui(self, container):

        """
        When the plugin is activated, a GUI is built and packed into the given 
        container.  This consists of four buttons:
            - "Match FP": to rotate the sub-field to match the orientation of the focal plane;
            - "Restore": to go back to the original orientation of the sub-field (with the readout
              register at the bottom of the CCD);
            - "Save": to open this image next time with the current orientation;
            - "Close": to close the plugin (without saving the current orientation).

        :param container: Container in which to pack the GUI.
        """

        vbox = Widgets.VBox()
        vbox.set_border_width(1)
        vbox.set_spacing(1)

        # No FITS file loaded

        if self.fitsimage.get_image() is None:

            text = "No image has been loaded into the current channel.  Please, close this plugin by pressing the \"Close\" button."
            no_image_label = Widgets.Label(text)
            vbox.add_widget(no_image_label)

        # FITS file loaded

        else:

            header = self.fitsimage.get_image().get_header()
            keys = list(header.keys())

            if "CROTA2" in keys:

                self.rotation_angle = header.get_card("CROTA2")["value"]
            
            else:
                text = "The loaded FITS file does not contain the CROTA2 keyword in the header.  Please, close this plugin by pressing the \"Close\" button."
                no_crota2_label = Widgets.Label(text)
                vbox.add_widget(no_crota2_label)


        buttons = Widgets.HBox()
        buttons.set_border_width(4)
        buttons.set_spacing(3)

        # Match button

        match_button = Widgets.Button("Match FP")
        match_button.set_tooltip("Rotate the sub-field to match the orientation of the focal plane")
        match_button.add_callback('activated', lambda w: self.match())
        buttons.add_widget(match_button)

        # Save button

        save_button = Widgets.Button("Save settings")
        save_button.set_tooltip("Open this image next time with the current orientation")
        save_button.add_callback("activated", lambda w: self.save_settings())
        buttons.add_widget(save_button)

        # Restore button

        restore_button = Widgets.Button("Restore")
        restore_button.set_tooltip("Go back to the original orientation of the sub-field (with the readout register at the bottom of the CCD)")
        restore_button.add_callback('activated', lambda w: self.restore())
        buttons.add_widget(restore_button)

        # Close button

        close_button = Widgets.Button("Close")
        close_button.set_tooltip("Close this plugin")
        close_button.add_callback('activated', lambda w: self.close())
        buttons.add_widget(close_button)

        vbox.add_widget(buttons)

        container.add_widget(vbox, stretch=1)

    def close(self):

        """
        Close action (to execute when the "Close" button is pushed).
        """
        
        self.fv.stop_local_plugin(self.chname, str(self))

        return True

    def match(self):

        """
        Rotate the image (in the Ginga reference viewer) over the angle, specified by the CROTA2
        keyword in the header of the FITS file.
        """

        self.t_.set(rot_deg=self.rotation_angle)
        self.fitsimage.center_image()

        return True

    def restore(self):

        """
        Go back to the original orientation of the sub-field (with the readout register
        at the bottom of the CCD)
        """

        self.t_.set(rot_deg=0.0)
        self.fitsimage.center_image()

        return True

    def save_settings(self):

        """
        Save the current settings, to open the image next time with the current orientation.
        """

        self.t_.save()


    def __str__(self):

        """
        Returns the string representation of this plugin.  This needs to be the small-case
        version of the class name in order for the Ginga reference viewer to pick it up.
        """

        return "matchfocalplane"
