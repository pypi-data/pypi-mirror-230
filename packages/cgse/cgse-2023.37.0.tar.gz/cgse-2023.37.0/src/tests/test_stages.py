import contextlib
import logging
from collections import namedtuple
from functools import lru_cache

import pytest
from pytest import approx

from egse.device import DeviceConnectionError
from egse.stages.huber.smc9300 import HuberSMC9300Controller
from egse.system import Timer

LOGGER = logging.getLogger("egse.tests.stages.huber")

BIG_ROTATION_STAGE = 1
SMALL_ROTATION_STAGE = 2
TRANSLATION_STAGE = 3

device = namedtuple("device", ["axis", "interface", "slew_speed"])


@pytest.fixture(params=[(BIG_ROTATION_STAGE, 20_000), (SMALL_ROTATION_STAGE, 20_000)])
# @lru_cache  # This decorator interferes with the fixture!!
def setup_rotation_stage(request):
    stage = HuberSMC9300Controller()
    with contextlib.suppress(DeviceConnectionError):
        stage.connect()

    if not stage.is_connected():
        pytest.skip("setup_rotation_stage: could not connect to device, test skipped.")

    axis = request.param[0]
    slew_speed = request.param[1]

    stage.set_slew_speed(axis, slew_speed)

    yield device(axis, stage, slew_speed)

    stage.disconnect()


@pytest.fixture(params=[(TRANSLATION_STAGE, 20_000)])
# @lru_cache  # This decorator interferes with the fixture!!
def setup_translation_stage(request):
    stage = HuberSMC9300Controller()
    with contextlib.suppress(DeviceConnectionError):
        stage.connect()

    if not stage.is_connected():
        pytest.skip("setup_translation_stage: could not connect to device, test skipped.")

    axis = request.param[0]
    slew_speed = request.param[1]

    stage.set_slew_speed(axis, slew_speed)

    yield device(axis, stage, slew_speed)

    stage.disconnect()


def test_goto(setup_rotation_stage: device):
    """
    First goto the zero position and check for both current position and current
    encoder position to be 0.0 with tolerances. Then goto an arbitrary position
    (7.4233 degrees and 12.3332 degrees) and again check the current position
    and the current encoder position. Finally, go back to the zero position.

    This test will be executed for both the big and the small rotation stage. See fixture.

    Args:
        setup_rotation_stage: setup either direct control or the simulator

    Returns:
        None.

    """

    LOGGER.warning(f"{type(setup_rotation_stage)=}")

    axis = setup_rotation_stage.axis
    rot = setup_rotation_stage.interface
    slew_speed = setup_rotation_stage.slew_speed

    rel_tolerance = 0.001
    abs_tolerance = 0.001

    rot.goto(axis, 0.0)

    assert rot.get_slew_speed(axis) == slew_speed
    assert rot.get_current_position(axis) == approx(0.0, rel=rel_tolerance, abs=abs_tolerance)
    assert rot.get_current_encoder_position(axis) == approx(0.0, rel=rel_tolerance, abs=abs_tolerance)

    pos = 7.4233

    rot.goto(axis, pos)

    assert rot.get_current_position(axis) == approx(pos, rel=rel_tolerance, abs=abs_tolerance)
    assert rot.get_current_encoder_position(axis) == approx(pos, rel=rel_tolerance, abs=abs_tolerance)

    pos = 12.3332

    rot.goto(axis, pos)

    assert rot.get_current_position(axis) == approx(pos, rel=rel_tolerance, abs=abs_tolerance)
    assert rot.get_current_encoder_position(axis) == approx(pos, rel=rel_tolerance, abs=abs_tolerance)

    rot.goto(axis, 0.0)


def test_moving_10deg_timer(setup_rotation_stage: device):

    LOGGER.warning(f"{type(setup_rotation_stage)=}")

    axis = setup_rotation_stage.axis
    rot = setup_rotation_stage.interface
    slew_speed = setup_rotation_stage.slew_speed

    rel_tolerance = 0.001
    abs_tolerance = 0.001

    rot.goto(axis, 0.0)

    assert rot.get_slew_speed(axis) == slew_speed
    assert rot.get_current_position(axis) == approx(0.0, rel=rel_tolerance, abs=abs_tolerance)
    assert rot.get_current_encoder_position(axis) == approx(0.0, rel=rel_tolerance, abs=abs_tolerance)

    pos = 10.0000

    with Timer():
        rot.goto(axis, pos)

    assert rot.get_current_position(axis) == approx(pos, rel=rel_tolerance, abs=abs_tolerance)
    assert rot.get_current_encoder_position(axis) == approx(pos, rel=rel_tolerance, abs=abs_tolerance)

    rot.goto(axis, 0.0)


def test_move(setup_rotation_stage: device):

    LOGGER.warning(f"{type(setup_rotation_stage)=}")

    axis = setup_rotation_stage.axis
    rot = setup_rotation_stage.interface
    slew_speed = setup_rotation_stage.slew_speed

    rel_tolerance = 0.001
    abs_tolerance = 0.001

    distance = 15.1234
    start = 5.1234

    rot.goto(axis, start)

    assert rot.get_slew_speed(axis) == slew_speed
    assert rot.get_current_encoder_position(axis) == approx(start, rel=rel_tolerance, abs=abs_tolerance)
    assert rot.get_current_position(axis) == approx(start, rel=rel_tolerance, abs=abs_tolerance)

    rot.move(axis, distance)

    assert rot.get_current_encoder_position(axis) == approx(start+distance, rel=rel_tolerance, abs=abs_tolerance)
    assert rot.get_current_position(axis) == approx(start+distance, rel=rel_tolerance, abs=abs_tolerance)

    rot.move(axis, -distance)

    assert rot.get_current_encoder_position(axis) == approx(start, rel=rel_tolerance, abs=abs_tolerance)
    assert rot.get_current_position(axis) == approx(start, rel=rel_tolerance, abs=abs_tolerance)

    rot.goto(axis, 0.0)


def test_goto_translation(setup_translation_stage: device):

    LOGGER.warning(f"{type(setup_translation_stage)=}")

    axis = setup_translation_stage.axis
    trans = setup_translation_stage.interface
    slew_speed = setup_translation_stage.slew_speed

    rel_tolerance = 0.001
    abs_tolerance = 0.001

    start = 0.0

    trans.goto(axis, start)

    assert trans.get_slew_speed(axis) == slew_speed
    assert trans.get_current_encoder_position(axis) == approx(start, rel=rel_tolerance, abs=abs_tolerance)
    assert trans.get_current_position(axis) == approx(start, rel=rel_tolerance, abs=abs_tolerance)

    pos = 20.0

    trans.goto(axis, pos)

    assert trans.get_current_encoder_position(axis) == approx(pos, rel=rel_tolerance, abs=abs_tolerance)
    assert trans.get_current_position(axis) == approx(pos, rel=rel_tolerance, abs=abs_tolerance)

    trans.goto(axis, 0.0)
