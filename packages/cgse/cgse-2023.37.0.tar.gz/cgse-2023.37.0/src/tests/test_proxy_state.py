from egse.config import find_file
from egse.dummy import ctrl_settings
from egse.process import SubProcess
from egse.proxy import Proxy


def test_proxy_no_cs():

    proxy = Proxy(endpoint="tcp://localhost:8888")

    assert proxy
    assert not proxy.is_cs_connected()
    assert not proxy.get_commands()


def test_proxy_after_cs_started():

    # This will try to connect to a non-existing control server

    proxy = Proxy(endpoint=f"tcp://localhost:{ctrl_settings.COMMANDING_PORT}")
    assert proxy
    assert not proxy.is_cs_connected()

    # now start the control server

    stub = SubProcess("Dummy Process", ["python", find_file("dummy_cs.py")])
    stub.execute()

    # Proxy should be connected now

    assert proxy.is_cs_connected()

    # Now connect to the CS and check if commands are loaded - they should not!

    assert not proxy.has_commands()
    assert not proxy.get_commands()

    # Now load thee commands from the CS

    proxy.load_commands()
    assert proxy.get_commands()

    proxy.disconnect_cs()

    assert stub.quit() == 0


def test_proxy_normal_behavior():

    stub = SubProcess("Dummy Process", ["python", find_file("dummy_cs.py")])
    stub.execute()

    proxy = Proxy(endpoint=f"tcp://localhost:{ctrl_settings.COMMANDING_PORT}")
    assert proxy.is_cs_connected()
    assert proxy.get_commands()

    assert stub.quit() == 0
