from pathlib import Path

import pytest

from egse.obsid import ObservationIdentifier
from egse.obsid import TEST_LAB
from egse.obsid import TEST_LAB_SETUP

HERE = Path(__file__).parent.resolve()


def test_construction():

    with pytest.raises(ValueError):
        _ = ObservationIdentifier()

    obsid_1 = ObservationIdentifier("CSL", 42, 654321)
    obsid_2 = ObservationIdentifier("KUL", 42, 1212121)

    assert obsid_1 != obsid_2
    assert obsid_1 == ObservationIdentifier("CSL", 42, 654321)

    with pytest.raises(ValueError):
        _ = ObservationIdentifier("x", "y", "")

    with pytest.raises(ValueError):
        _ = ObservationIdentifier("x", "y", "z")


def test_create_from_string():

    obsid = ObservationIdentifier.create_from_string("LID_1111_2222")

    assert obsid.lab_id == "LID"
    assert obsid.setup_id == 1111
    assert obsid.test_id == 2222

    with pytest.raises(ValueError):
        obsid = ObservationIdentifier.create_from_string("LID::SID::TID")

    with pytest.raises(ValueError):
        obsid = ObservationIdentifier.create_from_string("")

    with pytest.raises(TypeError):
        obsid = ObservationIdentifier.create_from_string()


def test_str():
    obsid = ObservationIdentifier("CSL", 42, 654321)

    assert str(obsid) == "CSL_00042_654321"


def test_hashable_set():
    obsid_1 = ObservationIdentifier("CSL", 42, 654321)
    obsid_2 = ObservationIdentifier("KUL", 42, 1212121)

    s = {obsid_1, obsid_2}

    assert obsid_1 in s
    assert obsid_2 in s

    s.add(obsid_1)

    assert len(s) == 2


def test_create_id():

    from egse.obsid import TEST_LAB_SETUP, LAB_SETUP_TEST

    obsid = ObservationIdentifier("CSL", 53, 3225)

    assert obsid.create_id() == "CSL_00053_03225"
    assert obsid.create_id(order=LAB_SETUP_TEST) == "CSL_00053_03225"
    assert obsid.create_id(order=TEST_LAB_SETUP) == "03225_CSL_00053"
    assert obsid.create_id(order=TEST_LAB) == "03225_CSL"

    assert obsid.create_id(order=TEST_LAB, camera_name="Brigand") == "03225_CSL_brigand"
    assert obsid.create_id(order=TEST_LAB, camera_name=None) == "03225_CSL"
    assert obsid.create_id(order=TEST_LAB, camera_name='') == "03225_CSL"

    assert obsid == ObservationIdentifier.create_from_string("CSL_00053_03225")
    assert obsid == ObservationIdentifier.create_from_string("03225_CSL_00053", order=TEST_LAB_SETUP)
    assert obsid == ObservationIdentifier.create_from_string("CSL_00053_03225", order=LAB_SETUP_TEST)

    with pytest.raises(ValueError):
        ObservationIdentifier.create_from_string("03225_CSL_00053", order=TEST_LAB)


def test_obsid_from_storage():

    from egse.obsid import obsid_from_storage

    assert obsid_from_storage(313, data_dir=str(HERE / "data"), site_id="CSL") == '00313_CSL'

    # Since obsid 313 was an old observation with a folder name without a camera ID, this should still be
    # found, even if a camera name is provided.

    assert obsid_from_storage(313, data_dir=str(HERE / "data"), site_id="CSL", camera_name="achel") == '00313_CSL'

    # Also very old observations with the setup id in their name shall still be matched.

    assert obsid_from_storage(243, data_dir=str(HERE / "data"), site_id="CSL") == '00243_CSL_00056'
    assert obsid_from_storage("00243_CSL", data_dir=str(HERE / "data")) == '00243_CSL_00056'
    assert obsid_from_storage("00243_CSL_00056", data_dir=str(HERE / "data")) == '00243_CSL_00056'
    assert obsid_from_storage(
        ObservationIdentifier.create_from_string("00243_CSL_00056", TEST_LAB_SETUP), data_dir=str(HERE / "data")
    ) == '00243_CSL_00056'

    assert obsid_from_storage(
        ObservationIdentifier.create_from_string("00423_IAS_00038", TEST_LAB_SETUP),
        data_dir=str(HERE / "data"),
        camera_name="Brigand",
    ) == '00423_IAS_brigand'

    assert obsid_from_storage('2080_SRON', data_dir=str(HERE / "data")) == '02080_SRON_00041'

    with pytest.raises(ValueError) as exc:
        obsid_from_storage(11, data_dir=str(HERE / "data"))
    with pytest.raises(ValueError) as exc:
        obsid_from_storage('UNKNOWN', data_dir=str(HERE / "data"))
    with pytest.raises(ValueError) as exc:
        obsid_from_storage('INVALID_OBSID', data_dir=str(HERE / "data"))
