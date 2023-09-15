"""
This module provides a (local) plugin for the Ginga reference viewer, to select which
exposure from which window will be shown.  The exposures of any given window, are
stored in extensions in the FITS file, with the same name.  By default, the image is
rotated to match the orientation of the focal-plane reference frame.  The orientation 
angle of the window/sub-field (and CCD) w.r.t. the focal-plane reference frame (in degrees)
is read from the "CROTA2" keyword of the header of that image.

To start the Ginga reference viewer, with this extra plugin, execute the following set of commands:

    $ mkdir $HOME/.ginga/plugins
    $ cp exposureselection.py $HOME/.ginga/plugins/ExposureSelection.py
    $ ginga --plugins=ExposureSelection --loglevel=20 --stderr --log=/tmp/ginga.log

The plugin will then be available via the "Operation" button in the Plugin Manager bar
(currently under "Custom").

Alternatively, you can start the image viewer with the command:

    $ ./bin/start-image-viewer.bash

This is the same as the Ginga reference viewer, with all the additional PLATO-specific
plugins.  These plugins will then be available via the "Operation" button in the Plugin Manager bar
(under "PLATO").
"""

import time
import re
import os
import numpy as np

from ginga.gw import Widgets
from ginga.misc import Future
from ginga import GingaPlugin
from ginga.util import iohelper


class ExposureSelection(GingaPlugin.LocalPlugin):

    def __init__(self, fv, fitsimage):

        """
        Initialisation of a new (local) plugin for the Ginga reference viewer, to choose
        a specific exposure for a specific window.  The names of the windows are stored in
        the "EXTNAME" keyword of the header of the individual HDUs.

        Called when the plugin is loaded from the first time.

        Args:
            - fv: Reference to the Ginga (reference viewer) shell.
            - fitsimage: Reference to the specific viewer object associated with
                         the channel on which the plugin is being invoked.
        """

        super(ExposureSelection, self).__init__(fv, fitsimage)

        self._windows = {}

        self.gui_up = False
        self.path = None
        self.file_obj = None

        self.t_ = self.fitsimage.get_settings()

    def build_gui(self, container):

        """
        When the plugin is activated, a GUI is built and packed into the given 
        container. This consists of the following elements:

            - label with the number of windows;
            - combobox to choose the window;
            - spinner to choose the exposure (for the current window);
            - close button.
        
        Args:
            - container: Container in which to pack the GUI.
        """

        vbox = Widgets.VBox()
        vbox.set_border_width(1)
        vbox.set_spacing(1)

        captions = [("Number of windows:", "llabel", "Num Windows Label", "llabel"),        # Label with the number of windows
                    ("Choose Window", "llabel", "Choose Window Combobox", "combobox"),      # Combobox to choose the window
                    ("Choose Exposure", "llabel", "Choose Exposure Spinner", "spinbutton"), # Spinner to choose the exposure (for the current window)
                    ("Spacer", "spacer"),
                    ("Align with focal plane reference frame", "checkbutton"),              # Checkbutton to align with the focal-plane reference frame
                    ("Spacer", "spacer"),
                    ("Close", "button")]                                             # Close button

        w, b = Widgets.build_info(captions, orientation="vertical")
        self.w.update(b)

        self.w.num_windows_label = b.num_windows_label
        self.w.num_windows_label.set_text("0")

        self.w.window_combobox = b.choose_window_combobox
        self.w.window_combobox.set_tooltip("Choose which window to view")

        self.w.exposure_spinner = b.choose_exposure_spinner
        self.w.exposure_spinner.set_tooltip("Choose which exposure to view (for the current window)")
        self.w.exposure_spinner.hide()

        self.w.alignment_checkbox = b.align_with_focal_plane_reference_frame
        self.w.alignment_checkbox.set_tooltip("Check to align images with focal-plane reference plane.  Uncheck to use CCD reference frame instead.")

        self.w.close_button = b.close
        self.w.close_button.add_callback('activated', lambda w: self.close())
            
        vbox.add_widget(w)
        container.add_widget(vbox, stretch=1)

        self.selected_window = None     # No window selected
        self.selected_exposure = None   # No exposure selected

    def start(self):

        """
        Update the plugin when a new FITS file is loaded.
        """

        self.resume()

    def resume(self):

        """
        Update the plugin when a new FITS file is loaded.
        """

        self.redo()

    def redo(self):

        """
        Update the plugin when a new FITS file is loaded.
        """

        self.current_image = self.channel.get_current_image()

        # No file loaded -> no action needed

        if self.current_image is None:
            return True
        
        # Path to the loaded file

        path = self.current_image.get('path', None)

        # Can't open file

        if path is None:
            self.fv.show_error("Cannot open image: no value for metadata key 'path'")
            return

        # ASDF file (instead of FITS) -> no action needed

        if path.endswith(".asdf"):
            return True 
        
        # New FITS file loaded

        if path != self.path:

            self.path = path

            # Close the previous file opener (if any)

            if self.file_obj is not None:

                try:
                    self.file_obj.close()
                except Exception:
                    pass
            
            self.file_obj = self.current_image.io
            self.file_obj.open_file(path)
            self.hdu_dct = self.file_obj.get_directory()

            self.build_window_list()

            self.w.num_windows_label.set_text(str(len(self._windows)))
            self.selected_window = sorted(self._windows)[0]
            self.w.exposure_spinner.show()
            self.selected_exposure = 1
            
            self.prepare_selection(self.w.window_combobox, self.w.exposure_spinner)
            self.prepare_alignment(self.w.alignment_checkbox)

            self.w.alignment_checkbox.set_state(True)

    def build_window_list(self):

        """
        Take stock of the different extension names occur in the FITS file, having
        image data in it (so the primary HDU is not included).  Each extension corresponds
        to a window and for each window we store the slice indices (as they occur in the
        FITS file) of the images corresponding to that window.  These slices correspond to
        the exposures of the window.
        """

        index = 0

        while True:

            info = self.hdu_dct.get(index, None)
                
            if info is None:
                break

            if info["htype"] == "ImageHDU":

                window = info["name"]

                if window.startswith("WINDOW"):

                    if window in self._windows:
                        self._windows[window].append(index)
                    else:
                        self._windows[window] = [index]
            
            index += 1

    def prepare_selection(self, window_combobox, exposure_spinner):
        """
        Make sure the given combobox can be used to choose the window and the
        given spinner can be used to choose the exposure.

        Args:
            - window_combobox: Combobox used to select the window.
            - exposure_spinner: Spinner used to select the exposure for the current window.
        """

        window_combobox.clear()

        sorted_windows = sorted(self._windows)

        for idx, d in enumerate(sorted_windows):
            if d.startswith("WINDOW"):
                window_combobox.append_text(d)

        self.select_window(window_combobox, 0, exposure_spinner)

        window_combobox.add_callback("activated", self.select_window, exposure_spinner)
        exposure_spinner.add_callback("value-changed", self.select_exposure)

    def select_window(self, window_combobox, selected_window, exposure_spinner):
        """
        Select the given window and update the spinner to select the exposure for this
        window.  When a new FITS file is loaded or when the currently selected exposure
        is not available for the newly selected window, the first exposure of the newly
        selected will be selected in the spinner and displayed in the central widget of the
        image viewer.

        Args:
            - window_combobox: Combobox used to select the window.
            - selected_window: Index (not the name!) of the new window selected by the
                               combobox.
            - exposure_spinner: Spinner used to select the exposure for the current window.
        """

        self.selected_window = self.w.window_combobox.get_text()

        # Update the range of exposures that can be selected for the newly selected window

        lower, upper = 1, len(self._windows[self.selected_window])
        exposure_spinner.set_limits(lower, upper, incr_value=1)

        # If the newly selected window doesn't have as many exposures as the index of the
        # previously selected exposure (for the previously selected window), select the
        # first exposure (counting of the exposures starts at 1, conform the FITS convention).
        # Otherwise, the same exposure will be selected as before (but for the newly selected
        # window instead).

        if self.selected_exposure > len(self._windows[self.selected_window]):
            self.selected_exposure = 1
        exposure_spinner.set_value(self.selected_exposure)
        
        # Convert the selected window and exposure to slice index in the FITS file

        slice_index = self._windows[self.selected_window][self.selected_exposure - 1]

        # Display the image in the central widget of the image viewer

        self.set_hdu(slice_index)

    def select_exposure(self, exposure_spinner, selected_exposure):

        """
        Display the given exposure in the central widget of the image viewer, if the value
        of the given spinner changes to the given value for the current window.

        Args:
            - exposure_spinner: Spinner used to select the exposure for the current window.
            - selected_exposure: New exposure selected by the given spinner.
        """

        self.selected_exposure = selected_exposure

        # Convert the selected window and exposure to slice index in the FITS file

        slice_index = self._windows[self.selected_window][selected_exposure - 1]

        # Display the image in the central widget of the image viewer

        self.set_hdu(slice_index)

    def set_hdu(self, slice_index):
        """
        Display the given slice from the FITS file in the central widget of the image viewer.
        
        Args:
            - slice_index: Index of the slice that needs to be displayed.
        """

        self.logger.debug("Loading index #%d" % (slice_index))

        info = self.file_obj.get_info_idx(slice_index)
        aidx = (info.name, info.extver)                 # (window, exposure)

        if aidx not in self.hdu_dct:
            aidx = slice_index
        sfx = iohelper.get_hdu_suffix(aidx)

        name = self.current_image.get('name', iohelper.name_image_from_path(self.path))
        match = re.match(r'^(.+)\[(.+)\]$', name)
        if match:
            name = match.group(1)
        
        imname = name + sfx
        chname = self.chname
        chinfo = self.channel

        # The image is still in memory

        if imname in chinfo.datasrc:

            self.curhdu = slice_index
            self.fv.switch_name(chname, imname)

            return

        # The image is not in memory -> load it

        self.logger.debug("Index %d not in memory; refreshing from file" % (slice_index))

        def _load_idx(image):

            try:

                # Create a future for re-constituting this HDU

                future = Future.Future()
                future.freeze(self.fv.load_image, self.path, idx=aidx)
                image.set(path=self.path, idx=aidx, name=imname, image_future=future)

                self.fv.add_image(imname, image, chname=chname)
                self.curhdu = slice_index
                self.logger.debug("HDU #%d loaded." % (slice_index))

            except Exception as e:

                errmsg = "Error loading FITS HDU #%d: %s" % (slice_index, str(e))
                self.logger.error(errmsg)
                self.fv.show_error(errmsg, raisetab=True)

        self.file_obj.load_idx_cont(slice_index, _load_idx)

        if self.w.alignment_checkbox.get_state():

            self.align_hdu_with_focal_plane()

        else:

            self.align_hdu_with_ccd()

    def prepare_alignment(self, alignment_checkbox):

        """
        Make sure the checkbox can be used to choose whether to align with
        the focal-plane or the CCD reference frame.

        Args:
            - alignment_checkbox: Checkbox used to choose the alignment.
        """

        alignment_checkbox.add_callback("activated", self.align_hdu)

    def align_hdu(self, alignment_checkbox, is_checked):

        """
        Make sure the images in the central widget of the image viewer are showed aligned
        to either the focal-plane or CCD reference frame, depending on the state of the
        checkbox.

        Args:
            - alignment_checkbox: Checkbox used to choose the alignment.
            - is_checked: New state of the checkbox.
        """

        # Checked -> align with the focal-plane reference frame

        if is_checked:

            self.align_hdu_with_focal_plane()

        # Unchecked -> align with the CCD reference frame

        else:

            self.align_hdu_with_ccd()

    def align_hdu_with_focal_plane(self):

        """
        From now on, show the images in the central widget of the image viewer aligned
        with the focal-plane reference frame.  The rotation angle is read from the "CROTA2"
        keyword in the FITS header.
        """

        header = self.channel.get_current_image().get_header()
        # header = self.fitsimage.get_image().get_header()
        keys = list(header.keys())

        if "CROTA2" in keys:

            rotation_angle = header.get_card("CROTA2")["value"]
            self.t_.set(rot_deg=rotation_angle)
        
        else:
            # TODO
            pass

    def align_hdu_with_ccd(self):

        """
        From now on, show the images in the central widget of the image viewer aligned
        with the CCD reference frame (i.e. zero rotation).
        """

        self.t_.set(rot_deg=0)

    def close(self):

        """
        Close action (to execute when the "Close" button is pushed).
        """
        
        self.fv.stop_local_plugin(self.chname, str(self))

        return True

    def stop(self):

        """
        Stop the plugin.  Set the variables to None.
        """

        self.gui_up = False
        
        if self.file_obj is not None:
            try:
                self.file_obj.close()
            except Exception:
                pass
        
        self.file_obj = None
        self.path = None
        self.hdu_dct = None
        self._windows = None

        self.fv.show_status("")

    def __str__(self):
        return 'exposureselection'
