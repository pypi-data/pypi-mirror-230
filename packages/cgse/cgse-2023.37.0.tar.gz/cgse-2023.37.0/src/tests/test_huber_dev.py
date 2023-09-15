import logging

import pytest

from egse.device import DeviceConnectionError
from egse.device import DeviceTimeoutError
from egse.stages.huber.smc9300 import calculate_relative_movement
from egse.stages.huber.smc9300_devif import HuberSMC9300EthernetInterface

MODULE_LOGGER = logging.getLogger("egse.tests.test_huber")


def is_smc_connected():
    #   pytest.set_trace()

    try:
        huber = HuberSMC9300EthernetInterface()
        huber.connect()
    except (ValueError, DeviceConnectionError, DeviceTimeoutError) as exc:
        MODULE_LOGGER.info(f"SMC9300 not connected ({exc})")
        return False
    finally:
        huber.disconnect()

    return True


smc_connected = bool(is_smc_connected())


@pytest.mark.skipif(not smc_connected, reason="requires SMC9300 to be connected")
def test_constructor():
    huber = HuberSMC9300EthernetInterface()

    assert not huber.is_connected()


@pytest.mark.skipif(not smc_connected, reason="requires SMC9300 to be connected")
def test_connect():
    huber = HuberSMC9300EthernetInterface()
    huber.connect()

    assert huber.is_connected()


@pytest.mark.skipif(not smc_connected, reason="requires SMC9300 to be connected")
def test_disconnect():
    huber = HuberSMC9300EthernetInterface()
    huber.connect()

    assert huber.is_connected()

    huber.disconnect()

    assert not huber.is_connected()


@pytest.mark.skipif(not smc_connected, reason="requires SMC9300 to be connected")
def test_query():
    huber = HuberSMC9300EthernetInterface()
    huber.connect()

    out = huber.query("?conf1\r\n")  # get_configuration

    assert type(out) == bytes
    assert out.decode().startswith('# configuration settings of axis 1')

    huber.disconnect()


@pytest.mark.skipif(not smc_connected, reason="requires SMC9300 to be connected")
def test_write():
    huber = HuberSMC9300EthernetInterface()
    huber.connect()

    huber.write("cerr1\r\n")  # clear error on axis 1

    huber.disconnect()


def test_movement_direction():
    print()
    assert calculate_relative_movement(0, 30) == 30

    with pytest.raises(ValueError):
        assert calculate_relative_movement(0, 177) == 177
    assert calculate_relative_movement(0, 183) == -177
    assert calculate_relative_movement(0, 270) == -90

    assert calculate_relative_movement(0, -30) == -30
    assert calculate_relative_movement(0, -177) == -177

    with pytest.raises(ValueError):
        assert calculate_relative_movement(0, -183) == 177
    assert calculate_relative_movement(0, -270) == 90

    assert calculate_relative_movement(10, 30) == 20

    with pytest.raises(ValueError):
        assert calculate_relative_movement(10, 177) == 167
    assert calculate_relative_movement(10, 183) == -187
    assert calculate_relative_movement(10, 270) == -100

    assert calculate_relative_movement(-10, 30) == 40
    with pytest.raises(ValueError):
        assert calculate_relative_movement(-10, 177) == 187
    assert calculate_relative_movement(-10, 183) == -167
    assert calculate_relative_movement(-10, 270) == -80

    assert calculate_relative_movement(10, -30) == -40
    assert calculate_relative_movement(10, -177) == -187
    with pytest.raises(ValueError):
        assert calculate_relative_movement(10, -183) == 167
    assert calculate_relative_movement(10, -270) == 80

    assert calculate_relative_movement(-10, -30) == -20
    assert calculate_relative_movement(-10, -177) == -167
    with pytest.raises(ValueError):
        assert calculate_relative_movement(-10, -183) == 187
    assert calculate_relative_movement(-10, -270) == 100

    # setpoint can not fall in avoidance range

    with pytest.raises(ValueError):
        calculate_relative_movement(0, 178)
        calculate_relative_movement(0, 179)
        calculate_relative_movement(0, 180)
        calculate_relative_movement(0, 181)
        calculate_relative_movement(0, 182)

    assert calculate_relative_movement(-40, -30) == 10

    # Some tests around 180º

    assert calculate_relative_movement(170, 190) == -340
    assert calculate_relative_movement(170, -190) == 0
    assert calculate_relative_movement(-170, 190) == 0
    assert calculate_relative_movement(-170, -190) == 340

    assert calculate_relative_movement(190, 170) == 340
    assert calculate_relative_movement(190, -170) == 0
    assert calculate_relative_movement(-190, 170) == 0
    assert calculate_relative_movement(-190, -170) == -340

    # These should actually fail because current can also not be in avoidance
    # range.

    assert calculate_relative_movement(181, 193) == 12
    assert calculate_relative_movement(182, 193) == 11
    assert calculate_relative_movement(183, 193) == 10

    with pytest.raises(ValueError):
        calculate_relative_movement(193, 181)
        calculate_relative_movement(193, 182)
        calculate_relative_movement(193, 183)

    assert calculate_relative_movement(193, 184) == -9


def test_movement_direction_with_hardstop():

    assert calculate_relative_movement(0, 42, hardstop=45) == 42
    with pytest.raises(ValueError):
        calculate_relative_movement(0, 43, hardstop=45)
        calculate_relative_movement(0, 44, hardstop=45)
        calculate_relative_movement(0, 45, hardstop=45)
        calculate_relative_movement(0, 46, hardstop=45)
        calculate_relative_movement(0, 47, hardstop=45)
    assert calculate_relative_movement(0, 48, hardstop=45) == -312

    assert calculate_relative_movement(42, 48, hardstop=45.0) == -354.0
    assert calculate_relative_movement(48, 42, hardstop=45.0) == 354.0

    # Put the hardstop near 180º, say 179.316º

    assert calculate_relative_movement(170, 176, avoidance=3.1, hardstop=179.316) == 6
    assert calculate_relative_movement(170, 176.2, avoidance=3.1, hardstop=179.316) == pytest.approx(6.2)

    assert calculate_relative_movement(170, 176.216, avoidance=3.1, hardstop=179.316) == pytest.approx(6.216)

    with pytest.raises(ValueError):
        calculate_relative_movement(170, 176.217, avoidance=3.1, hardstop=179.316)

    assert calculate_relative_movement(170, 183, avoidance=3.1, hardstop=179.316) == pytest.approx(-347)
    assert calculate_relative_movement(170, 182.416, avoidance=3.1, hardstop=179.316) == pytest.approx(-347.584)


def test_issue_909_01():

    # Some edge cases

    assert calculate_relative_movement(0.0, 175) == pytest.approx(175.0)
    assert calculate_relative_movement(171, -171) == pytest.approx(-342.0)
    assert calculate_relative_movement(171, -171, hardstop=180, avoidance=0) == pytest.approx(-342.0)

    hardstop = 180.0
    avoidance = 3.0

    current = 0.0

    for target in range(360):
        if hardstop - avoidance < target < hardstop + avoidance:
            with pytest.raises(ValueError):
                calculate_relative_movement(
                    current, target, hardstop=hardstop, avoidance=avoidance)
        elif target >= hardstop + avoidance:
            assert calculate_relative_movement(
                current, target, hardstop=hardstop, avoidance=avoidance) == pytest.approx(-(360-target))
        else:
            assert calculate_relative_movement(
                current, target, hardstop=hardstop, avoidance=avoidance) == pytest.approx(target)


def test_issue_909_02():

    hardstop = 180.0
    avoidance = 3.0

    current = 0.0

    for target in range(-171, 172, 18):
        movement = calculate_relative_movement(
            current, target, hardstop=hardstop, avoidance=avoidance
        )

        if current == pytest.approx(0.0):
            assert movement < 0
            assert pytest.approx(movement) == - abs(target - current)
        else:
            assert movement > 0
            assert pytest.approx(movement) == abs(target - current)

        current = target

    assert current == pytest.approx(171)

    for target in range(-171, 172, 18):
        movement = calculate_relative_movement(
            current, target, hardstop=hardstop, avoidance=avoidance
        )

        if current == pytest.approx(171):
            assert movement < 0
            assert pytest.approx(movement) == - abs(target - current)
        else:
            assert movement > 0
            assert pytest.approx(movement) == abs(target - current)

        current = target


def test_issue_909_03():
    hardstop = 180.0
    avoidance = 3.0

    current = 171.0  # end of the circle measurement
    target = -167.34  # start of the full hartmann measurement

    movement = calculate_relative_movement(
        current, target, hardstop=hardstop, avoidance=avoidance
    )
    assert movement < 0
    assert pytest.approx(movement) == -338.34

    current = -171.0  # start of the circle measurement
    target = -167.34  # start of the full hartmann measurement

    movement = calculate_relative_movement(
        current, target, hardstop=hardstop, avoidance=avoidance
    )
    assert movement > 0
    assert pytest.approx(movement) == 3.66

    current = -171.0  # start of the circle measurement
    target = 167.34  # end of the full hartmann measurement

    movement = calculate_relative_movement(
        current, target, hardstop=hardstop, avoidance=avoidance
    )
    assert movement > 0
    assert pytest.approx(movement) == 338.34
