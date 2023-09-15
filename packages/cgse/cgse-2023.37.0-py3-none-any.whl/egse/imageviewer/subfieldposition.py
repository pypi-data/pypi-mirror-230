"""
This module provides a (local) plugin for the Ginga reference viewer, visualising
the position of the sub-field an image represents, on the focal plane.  The information
on the position of the sub-field is read from the header file of the loaded FITS file,
from the following keywords:

    * CCD_ID: code of the CCD on which the sub-field lies [1, 2, 3, 4];
    * (-CRPIX2, -CRPIX1): CCD coordinates (row, column) [pixels] of the origin
      of the sub-field in the CCD coordinate system for the CCD with the specified
      code (from the CCD_ID keyword);
    * NAXIS2: number of rows [pixels] in the sub-field;
    * NAXIS2: number of columns [pixels] in the sub-field.

To start the Ginga reference viewer, execute the following set of commands:

    $ mkdir $HOME/.ginga/plugins
    $ cp subfieldposition.py $HOME/.ginga/plugins/SubFieldPosition.py
    $ ginga --plugins=SubFieldPosition --loglevel=20 --stderr --log=/tmp/ginga.log

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

class SubFieldPosition(GingaPlugin.LocalPlugin):

    def __init__(self, fv, fitsimage):

        """
        Initialisation of a new (local) plugin for the Ginga reference viewer, to visualise 
        the position of the sub-field an image represents, on the focal plane.  The information
        on the position of the sub-field is read from the header file of the loaded FITS file
        Called when the plugin is loaded from the first time.

        Args:
            - fv: Reference to the Ginga (reference viewer) shell.
            - fitsimage: Reference to the specific viewer object associated with
                        the channel on which the plugin is being invoked.
        """

        super(SubFieldPosition, self).__init__(fv, fitsimage)

    def build_gui(self, container):

        """
        When the plugin is activated, a GUI is built and packed into the given 
        container.  This consists of a plot window, visualising the focal plane 
        (with a blue circle indicating the field-of-view) on which the sub-field
        will be drawn (if the required keywords are available in the FITS header),
        and a combobox to switch between coordinate systems (focal-plane coordinates,
        pixel coordinates, and field angles).

        Args:
            - container: Container in which to pack the GUI.
        """

        vbox = Widgets.VBox()
        vbox.set_border_width(1)
        vbox.set_spacing(1)

        self.focal_plane = FocalPlaneWidgetWithSubField()
        vbox.add_widget(self.focal_plane)

        captions = [("Close", "button")]

        w, b = Widgets.build_info(captions, orientation="vertical")
        self.w.update(b)

        self.w.close_button = b.close
        self.w.close_button.add_callback('activated', lambda w: self.close())

        vbox.add_widget(w)
        container.add_widget(vbox, stretch=1)

        self.redo()


    def redo(self):

        """
        Update the plugin when a new FITS file is loaded or a new image is shown in the 
        central widget of the image viewer.
        """
        
        current_image = self.channel.get_current_image()

        # No file loaded -> no action needed

        if current_image is None:

            return True

        # File loaded

        header = current_image.get_header()

        ccd_code = header.get_card("CCD_ID")["value"]               # CCD code
        zeropoint_row = -header.get_card("CRPIX2")["value"]         # Sub-field zeropoint row
        zeropoint_column = -header.get_card("CRPIX1")["value"]      # Sub-field zeropoint column
        num_rows = header.get_card("NAXIS2")["value"]               # Number of rows in the sub-field
        num_columns = header.get_card("NAXIS1")["value"]            # Number of columns in the sub-field
        
        self.focal_plane.focal_plane.set_subfield(ccd_code=ccd_code, zeropoint_row=zeropoint_row, zeropoint_column=zeropoint_column, num_rows=num_rows, num_columns=num_columns)

    def close(self):

        """
        Close action (to execute when the "Close" button is pushed).
        """
        
        self.fv.stop_local_plugin(self.chname, str(self))
        
        return True

    def __str__(self):

        """
        Returns the string representation of this plugin.  This needs to be the small-case
        version of the class name in order for the Ginga reference viewer to pick it up.
        """

        return "subfieldposition"
