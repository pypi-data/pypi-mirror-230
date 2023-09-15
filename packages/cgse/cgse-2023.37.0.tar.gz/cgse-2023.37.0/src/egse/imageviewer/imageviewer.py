"""
Version of the Ginga reference viewer with extra, PLATO-specific plugins. Currently
the following plugins have been implemented:

    * SubFieldPosition: visualising the position of the sub-field an image represents, on the focal plane;
    * MatchFocalPlane: rotating the image, to match the orientation of the focal-plane reference frame 
                       (rather than the CCD reference frame).

To start the image viewer execute the following command:

    $ ./bin/start-image-viewer.bash

This is the same as the Ginga reference viewer, with all the additional PLATO-specific
plugins.  These plugins will then be available via the `Operation` button in the Plugin Manager bar
(under `PLATO`).
"""

import ginga.rv.main as rv
from PyQt5.QtWidgets import QApplication
from ginga.misc.Bunch import Bunch
import sys
import os

from ginga.misc import Settings, log
from ginga.util import paths


class ImageViewer(rv.ReferenceViewer):
    # Plugins specifically for PLATO

    plato_plugins = [
        Bunch(module="SubFieldPosition", tab="Sub-Field Position", workspace="right", start=False,
              menu="Sub-field Position", category="PLATO", ptype="local"),
        Bunch(module="ExposureSelection", tab="Window and Exposure Selection", workspace="lleft", start=True,
              menu="Window and Exposure Selection", category="PLATO", ptype="local"),
    ]

    def __init__(self, sys_argv, layout=rv.default_layout):
        """
        Initialisation of the Ginga reference viewer, with additional PLATO-specific plugins.
        """

        super().__init__()

        self.plugins = self.plugins + self.plato_plugins


        self.add_default_plugins()
        self.add_separately_distributed_plugins()

        # Parse command line options with argparse module
        from argparse import ArgumentParser

        argprs = ArgumentParser(description="Run the image viewer.")
        self.add_default_options(argprs)
        argprs.add_argument('-V', '--version', action='version', version='%(prog)s {}'.format(rv.version.version))
        (options, args) = argprs.parse_known_args(sys_argv[1:])

        if options.display:
            os.environ['DISPLAY'] = options.display

        # Are we debugging this?
        if options.debug:

            import pdb

            pdb.run('viewer.main(options, args)')

        # Are we profiling this?
        elif options.profile:
            import profile

            print(("%s profile:" % sys_argv[0]))
            profile.runctx('viewer.main(options, args)', dict(options=options, args=args, viewer=viewer), {})

        else:

            # Create a logger
            logger = log.get_logger(name='ginga', options=options)

            # Get settings (preferences)
            basedir = paths.ginga_home
            if not os.path.exists(basedir):
                try:
                    os.mkdir(basedir)
                except OSError as e:
                    logger.warning("Couldn't create ginga settings area (%s): %s" % (basedir, str(e)))
                    logger.warning("Preferences will not be able to be saved")

            self.main(options, args)

        # prefs = Settings.Preferences(basefolder=basedir, logger=logger)
        # settings = prefs.create_category('plato')
        # settings.set_defaults(channel_prefix="PLATO")
        # settings.load(onError='silent')

# class ImageViewer(rv.ReferenceViewer):
#
#     # Plugins specifically for PLATO
#
#     plato_plugins = [
#         Bunch(module="SubFieldPosition", tab="Sub-Field Position", workspace="right", start=False, menu="Sub-field Position", category="PLATO", ptype="local"),
#         Bunch(module="ExposureSelection", tab="Window and Exposure Selection", workspace="lleft", start=True, menu="Window and Exposure Selection", category="PLATO", ptype="local"),
#     ]
#
#
#     def __init__(self, layout=rv.default_layout):
#
#         """
#         Initialisation of the Ginga reference viewer, with additional PLATO-specific plugins.
#         """
#
#         super().__init__()
#
#         self.plugins = self.plugins + self.plato_plugins
#
#
# def image_viewer(sys_argv):
#
#     """
#     Create the image viewer from the command line.
#
#     Args:
#         - sys_argv: Command line arguments.
#     """
#
#     viewer = ImageViewer(layout=rv.default_layout)
#
#     viewer.add_default_plugins()
#     viewer.add_separately_distributed_plugins()
#
#     # Parse command line options with argparse module
#     from argparse import ArgumentParser
#
#     argprs = ArgumentParser(description="Run the image viewer.")
#     viewer.add_default_options(argprs)
#     argprs.add_argument('-V', '--version', action='version',
#                         version='%(prog)s {}'.format(rv.version.version))
#     (options, args) = argprs.parse_known_args(sys_argv[1:])
#
#
#     if options.display:
#         os.environ['DISPLAY'] = options.display
#
#     # Are we debugging this?
#     if options.debug:
#         import pdb
#
#         pdb.run('viewer.main(options, args)')
#
#     # Are we profiling this?
#     elif options.profile:
#         import profile
#
#         print(("%s profile:" % sys_argv[0]))
#         profile.runctx('viewer.main(options, args)',
#                        dict(options=options, args=args, viewer=viewer), {})
#
#     else:
#
#         # Create a logger
#         logger = log.get_logger(name='ginga', options=options)
#
#         # Get settings (preferences)
#         basedir = paths.ginga_home
#         if not os.path.exists(basedir):
#             try:
#                 os.mkdir(basedir)
#             except OSError as e:
#                 logger.warning(
#                     "Couldn't create ginga settings area (%s): %s" % (
#                         basedir, str(e)))
#                 logger.warning("Preferences will not be able to be saved")
#
#         viewer.main(options, args)
#
#         # prefs = Settings.Preferences(basefolder=basedir, logger=logger)
#         # settings = prefs.create_category('plato')
#         # settings.set_defaults(channel_prefix="PLATO")
#         # settings.load(onError='silent')


def main():

    args = list(sys.argv)

    app = QApplication(args)

    # view = image_viewer(sys.argv)
    view = ImageViewer(sys.argv)
    view.show()

    return app.exec_()


if __name__ == '__main__':
        sys.exit(main())
   # image_viewer(sys.argv)