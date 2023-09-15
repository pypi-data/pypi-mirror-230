"""
In this unit test we try to check that certain imports and function do not take too much time,
especially imports of the whole system.
"""

import egse
from egse.state import GlobalState
from egse.confman import ConfigurationManagerProxy
from egse.confman import is_configuration_manager_active


def test_system_import():

    import egse.system as system

    with system.Timer("egse.system"):
        print(f"{system.get_system_stats() = }")
        print(f"{system.get_system_name() = }")


def test_env_import():

    import egse.env as env

    print(f"{env.get_data_storage_location() = }")


def test_setup_import():

    import egse.system as system

    with system.Timer("egse.setup"):
        import egse.setup as setup

    # This first call takes about 1.5s and is what I want to solve

    with system.Timer("load_setup"):
        # print(f"{setup.load_setup() = }")
        print(f"{GlobalState.load_setup() = }")

    # Second time this is called, it takes only a few milliseconds

    with system.Timer("load_setup"):
        print(f"{setup.load_setup() = }")
