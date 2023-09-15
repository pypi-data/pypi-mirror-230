from datetime import timedelta

from egse.obs import Observation


def test_default_constructor():

    obs = Observation()

    assert obs.duration == timedelta(seconds=6.25)
    assert obs.end_time == obs.start_time + timedelta(milliseconds=6250)
