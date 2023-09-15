import numpy as np
import pytest

from egse.coordinates import ReferenceFrame
from egse.coordinates.refmodel import ReferenceFrameModel


def test_construction():

    model = ReferenceFrameModel()

    assert len(model) == 0

    model = ReferenceFrameModel({"Master": ReferenceFrame.createMaster()})

    assert len(model) == 1

    # This should just be ignored and log a warning message.

    model.remove_frame("B")

    model_dict = model.serialize()

    assert "Master" in model_dict
    assert model_dict["Master"] == (
        "ReferenceFrame//([0.0000, 0.0000, 0.0000] | "
        "[0.0000, -0.0000, 0.0000] | Master | Master | [])"
    )

    model.add_frame("A", translation=[0.0, 0.0, 1.0], rotation=[0.0, 0.0, 0.0], ref="Master")

    with pytest.raises(KeyError):
        model.add_frame("A", translation=[0.0, 0.0, 1.0], rotation=[0.0, 0.0, 0.0], ref="Master")

    model.add_link("A", "Master")

    model_dict = model.serialize()

    print(model)

    assert len(model_dict) == len(model) == 2
    assert "A" in model_dict
    assert "A" in model


def test_construction_from_list():

    rot_config = "sxyz"
    master = ReferenceFrame.createMaster()

    a_ref = ReferenceFrame(
        transformation=np.identity(4), ref=master, name="a_ref", rot_config=rot_config
    )
    a_ref.addLink(master)

    b_ref = ReferenceFrame(
        transformation=np.identity(4), ref=a_ref, name="b_ref", rot_config=rot_config
    )

    c_ref = ReferenceFrame.fromTranslationRotation(
        [-2, -2, -2], [-3, -4, -5], rot_config=rot_config, ref=b_ref, name="c_ref"
    )
    c_ref.addLink(b_ref)
    c_ref.addLink(a_ref)

    d_ref = ReferenceFrame(
        transformation=np.identity(4), ref=c_ref, name="d_ref", rot_config=rot_config
    )

    model_list = [a_ref, b_ref, c_ref, d_ref, master]

    model = ReferenceFrameModel(model_list)

    assert "a_ref" in model
    assert "b_ref" in model
    assert "c_ref" in model
    assert "Master" in model

    print(model)


def test_add_frame_from_transformation():

    model = ReferenceFrameModel()

    model.add_master_frame()
    model.add_frame("a_ref", transformation=np.identity(4), ref="Master")
    model.add_link("a_ref", "Master")

    print(model)


def test_move_absolute():

    model = ReferenceFrameModel()

    model.add_master_frame()
    model.add_frame("A", translation=[4, 0, 2], rotation=[0, 0, 0], ref="Master")
    model.add_frame("B", translation=[-2, 0, 7], rotation=[0, 0, 0], ref="Master")

    print(model)

    model.move_absolute_self("A", [1, 0, 1], [0, 0, 0])

    print(model)

    model.add_link("A", "B")

    model.move_absolute_self("A", [-1, 0, 1], [0, 0, 0])

    print(model)

    # FIXME:
    #   This should not be possible, because 'A' and 'B' are linked.

    model.move_absolute_in_other("B", "A", [1, 0, 1], [0, 0, 0])

    print(model)
