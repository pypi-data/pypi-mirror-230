import pytest

from egse.filterwheel import FilterWheelError


@pytest.fixture
def get_filter_wheel():
    try:
        from egse.filterwheel.eksma.fw8smc4 import FilterWheel8SMC4Controller

        fw = FilterWheel8SMC4Controller()

        # FIXME:
        #   the connect method doesn't throw a ConnectionError when the device is not connected.

        fw.connect()
        fw.disconnect()

        return FilterWheel8SMC4Controller

    except FilterWheelError:
        from egse.filterwheel.eksma.fw8smc4 import FilterWheel8SMC4Simulator

        return FilterWheel8SMC4Simulator()


@pytest.mark.skip("This test results in several errors")
def test_connection(get_filter_wheel):

    fw = get_filter_wheel()

    print("***connection test started***")

    fw.connect()

    try:
        # FIXME:
        #   The get_id() is not a method of the FilterWheel, but of the EthernetInterface
        _id = fw.get_id()
        print("Is_connected?:", fw.is_connected())

    except FilterWheelError:
        assert False
    finally:
        print("*** end of test sequence ***")
        fw.disconnect()
