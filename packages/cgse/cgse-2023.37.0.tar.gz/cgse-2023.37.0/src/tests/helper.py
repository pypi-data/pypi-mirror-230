"""
This module provides helper functions for the unit test scripts. Do not use these functions
in your production code.
"""

# This module contains helper functions for making the unit tests work independently of any production setup.
# The Setup that is loaded from GlobalState would normally be provided by the configuration mananger (a server app)
# and provide devices that talk to the actual hardware. In the test scripts we do not want this behavior and the
# Setup is therefore loaded from the test_setup.yaml file and uses the device simulators.

from pathlib import Path

from egse.state import GlobalState
from egse.config import find_file, find_root


def load_test_setup():
    yaml_file = find_file(name='test_setup.yaml', in_dir='tests/data',
                          root=find_root(Path(__file__).resolve(), tests=('LICENSE',)))
    GlobalState._reload_setup_from(yaml_file)

