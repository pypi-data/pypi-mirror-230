"""
This module provides functions and classes to extract and mosaic windows from a CCD image.

Windowing is used to define areas in the CCD images that need to be down-linked as imagettes.
The F-FEE and the N-FEE will use windowing to minimize the size of data packets sent to the
F-DPU and N-DPU. A `WindowList` is used by the FEE and DPU to extract these imagettes from
the full CCD image and to re-generate the CCD image from the individual imagettes.
"""
import logging
from operator import itemgetter

import numpy as np

from egse.settings import Settings

logger = logging.getLogger(__name__)

win_settings = Settings.load("Windowing")


class WindowSizeError(Exception):
    """Raised when the requested window sizes are out-of-bounds."""
    pass


class CCDIndexError(KeyError):
    """Raised when the CCD index is out-of-bounds."""
    pass


def extract_window_data(ccd_image: np.array, x_coord: int, y_coord: int, x_size: int, y_size: int, ccd_side: int) -> np.array:
    """
    Extract the window data from the given image.

    Right and left side of the CCD have separate coordinate systems. The origin of both
    coordinate systems is the first pixel read from the CCD. See FEE-DPU-IF-900 in the DPU-FEE
    interface document (PLATO-DLR-PL-IC-002).

    Parameters:

    * **ccd_image**: ndarray - a two-dimensional array that contains the full image
    * **x_coord**: int - x-coordinate for the requested window
    * **y_coord**: int - y-coordinate for the requested window
    * **x_size**: int - x-size of the requested window
    * **y_size**: int - y-size of the requested window
    * **ccd_side**: int - the CCD side (0 is left, 1 is right)

    Returns: two-dimensional imagette (small window extracted from the full image)
    """

    # TODO
    #   - What is the full image? Are the scan maps stripped off?
    #   - The origin of the coordinate frame used to define the window is located in the serial pre-scan (not on the
    #     CCD) and starts from the first row in the image area (which is not necessarily the same as v_start)

    logger.debug("ccd size x, y = {}, {}".format(ccd_image.shape[0], ccd_image.shape[1]))
    logger.debug("x_size, y_size: {}, {}".format(x_size, y_size))
    logger.debug("x_coord, y_coord, ccd_side: {}, {}, {}".format(x_coord, y_coord, ccd_side))

    if ccd_side == win_settings.CCD_SIDE_LEFT:
        x1 = x_coord
        x2 = x_coord + x_size
        y1 = y_coord
        y2 = y_coord + y_size
        logger.debug("x1, x2, y1, y2 = {}, {}, {}, {}".format(x1, x2, y1, y2))
        im = ccd_image[y1:y2, x1:x2]
    elif ccd_side == win_settings.CCD_SIDE_RIGHT:
        ccd_x_size = ccd_image.shape[0]
        ccd_y_size = ccd_image.shape[1]
        x1 = ccd_x_size - x_coord - x_size
        x2 = ccd_x_size - x_coord
        y1 = y_coord
        y2 = y_coord + y_size
        logger.debug("x1, x2, y1, y2 = {}, {}, {}, {}".format(x1, x2, y1, y2))
        im = ccd_image[y1:y2, x1:x2]
    else:
        raise ValueError(f"CCD side argument should be 0 (left) or 1 (right), {ccd_side} was given.")

    return im


class WindowList:
    """
    The WindowList contains the window list for the FEE for one CCD.

    A window is defined for a specific CCD, so there are four window lists.

    Each element contains the coordinates for the window and the CCD side.  The size of the windows is identical for all
    windows on a CCD and can be configured between 2x2 and 32x32 [default size is 10x10]. The window does not need to
    be quadratic, i.e. x-size can be different from y-size.

    **Developer information**

    The internal representation of the window list is:

        set((x_coord, y_coord, ccd_side), (x_coord, y_coord, ccd_side), ...)

    """

    def __init__(self):
        """ Create an empty set"""

        # A set is used for the internal representation of the window list, that
        # prevents adding duplicate elements to the list.

        self._window_list = set()

        # Default window size in read from the global Settings

        self._window_x_size = win_settings.DEFAULT_WINDOW_SIZE
        self._window_y_size = win_settings.DEFAULT_WINDOW_SIZE

    def __str__(self):

        def _pp(list_):
            """Pretty print a large list."""
            if len(list_) > 10:
                # FIXME: the representation could be better here...when time allows
                return (
                    f"[{list_[0]}, {list_[1]}, {list_[2]}, {list_[3]}, {list_[4]}"
                    f", ..., "
                    f"{list_[-2]}, {list_[-1]}]"
                )
            else:
                return str(list_)

        return (
            f"Window size = ({self._window_x_size}, {self._window_y_size})\n"
            f"Window List CCD 1: len={self.get_window_count(1)}, {_pp(self.get_window_list_for_ccd(1))}\n"
            f"Window List CCD 2: len={self.get_window_count(2)}, {_pp(self.get_window_list_for_ccd(2))}\n"
            f"Window List CCD 3: len={self.get_window_count(3)}, {_pp(self.get_window_list_for_ccd(3))}\n"
            f"Window List CCD 4: len={self.get_window_count(4)}, {_pp(self.get_window_list_for_ccd(4))}\n"
        )

    def get_window_list(self):
        """ Return the window list.

        The list is a set of tuples, where each tuple contains the following information regarding one window:

            (x, y, ccd_side)

        The window list is sorted on y-coordinates first and x_coordinate second.
        """

        return sorted(self._window_list, key=itemgetter(1, 0))

    def add_window(self, x: int, y: int, ccd_side):
        """ Add a window to the window list.

        The window is appended to the list, which renders the list unsorted.  Use the `sort()` method after all windows
        have been added.

        Args:
            - x: Column or x-coordinate of the corner of the window closest to the readout node.
            - y: Row or y-coordinate of the corner of the window closest to the readout node.
            - ccd_side: CCD side.
        """

        # The window lists should be sorted first on the Y coordinate (rows), then the X-coordinate (columns).
        #
        # Internally however, the sets are not sorted because it would take too much time to keep the sets
        # sorted when this is only needed when the actual window list is requested by the caller.
        # Remember a list can take up to 100_000 elements.
        #
        # When a window list is requested using the `get_window_list()` method, a properly sorted list
        # will be returned.

        self._window_list.add((x, y, ccd_side))

    def get_window_count(self) -> int:
        """ Return the number of windows in the list.

        Returns: Number of windows.
        """

        return len(self._window_list)

    def set_window_size(self, x_size, y_size):
        """ Set a new window size.

        All windows have the same size. `x_size` and `y_size` do not have to be equal. The given size for both x and y
        has to be within the range [2-32] inclusive.

        Args:
            - x_side: Window size on the x-axis [pixels].
            - y_side: Window size on the y-axis [pixels].

        Raises a **WindowSizeError** when a given size is out of range.
        """

        if win_settings.MIN_WINDOW_SIZE <= x_size <= win_settings.MAX_WINDOW_SIZE:

            self._window_x_size = x_size

        else:

            raise WindowSizeError(f"Window size shall be [2, 32], {x_size} was given for x_size.")

        if win_settings.MIN_WINDOW_SIZE <= y_size <= win_settings.MAX_WINDOW_SIZE:

            self._window_y_size = y_size

        else:

            raise WindowSizeError(f"Window size shall be [2, 32], {y_size} was given for y_size.")

    def get_window_size(self):
        """ Return a tuple (x_size, y_size) containing the window size in pixels.

        Returns: Tuple with the window size (x_size, y_size) [pixels].
        """

        return self._window_x_size, self._window_y_size
