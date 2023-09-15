from egse.config import find_file
from egse.powermeter.thorlabs.pm100a import ThorlabsPM100Proxy
from egse.process import SubProcess
from egse.services import ServiceProxy
from egse.settings import Settings

ctrl_settings = Settings.load("Thorlabs PM100 Control Server")


def test_thorlabs_proxy():

    stub = SubProcess(
        "Dummy Process",
        ["python", find_file('pm100a_cs.py', in_dir='powermeter/thorlabs')], ["start", "--sim"])

    stub.execute()

    pm100 = ThorlabsPM100Proxy()
    pm100.ping()

    proxy = ServiceProxy(ctrl_settings)

    assert 'get_value' in pm100.get_commands()

    assert 0.0 <= pm100.get_value() <= 100.0

    pm100.disconnect()

    proxy.quit_server()
    proxy.disconnect_cs()

    assert stub.quit() == 0
