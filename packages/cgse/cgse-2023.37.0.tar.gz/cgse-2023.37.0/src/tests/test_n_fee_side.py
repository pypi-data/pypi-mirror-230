import pickle
from enum import IntEnum

import pytest

from egse.setup import Setup
from egse.state import GlobalState


@pytest.fixture
def n_fee_side():
    return Setup.from_dict({"E": 0, "F": 1})


@pytest.fixture
def n_fee_side_ex():
    return Setup.from_dict({"E": 0, "E_SIDE": 0, "F": 1, "F_SIDE": 1})


@pytest.fixture
def n_fee_side_from_setup():
    return GlobalState.setup.camera.fee.ccd_sides.enum


def test_n_fee_side_access(n_fee_side, n_fee_side_from_setup):

    assert n_fee_side.E == 0
    assert n_fee_side.F == 1

    x = n_fee_side_from_setup

    assert x.E == 0
    assert x.F == 1


def test_n_fee_side_ex_access(n_fee_side_ex, n_fee_side_from_setup):

    assert n_fee_side_ex.E == n_fee_side_ex.E_SIDE
    assert n_fee_side_ex.F == n_fee_side_ex.F_SIDE

    x = n_fee_side_from_setup

    assert x.E == x.E_SIDE == x.RIGHT_SIDE
    assert x.F == x.F_SIDE == x.LEFT_SIDE


def test_n_fee_side_ex_pickle(n_fee_side_ex):

    x = pickle.dumps(n_fee_side_ex)
    y = pickle.loads(x)

    assert n_fee_side_ex.E == y.E == y.E_SIDE
    assert n_fee_side_ex.F == y.F == y.F_SIDE

    x = pickle.dumps(n_fee_side_ex.E)
    y = pickle.loads(x)

    assert y == n_fee_side_ex.E_SIDE


def test_n_fee_side_from_setup_pickle(n_fee_side_from_setup):

    with pytest.raises(pickle.PicklingError):
        x = pickle.dumps(n_fee_side_from_setup)
        y = pickle.loads(x)

    with pytest.raises(pickle.PicklingError):
        x = pickle.dumps(n_fee_side_from_setup.E)
        y = pickle.loads(x)

    x = pickle.dumps(n_fee_side_from_setup.E.value)
    y = pickle.loads(x)

    assert y == n_fee_side_from_setup.E


def test_n_fee_side_from_setup_name(n_fee_side_from_setup):

    assert n_fee_side_from_setup.F.name == "F"
    assert n_fee_side_from_setup.E.name == "E"
    assert n_fee_side_from_setup.F_SIDE.name == "F"
    assert n_fee_side_from_setup.E_SIDE.name == "E"


def test_n_fee_side_ex_name(n_fee_side_ex):

    # There is no equivalent for knowing the name of an Enum value

    with pytest.raises(AttributeError):
        assert n_fee_side_ex.E.name == "E"


class FEE_SIDE(IntEnum):
    def __setstate__(self, state):
        print(f"inside {self.__class__.__name__}.__setstate()")
        print(f"{state = }")

    def __getstate__(self):
        print(f"inside {self.__class__.__name__}.__getstate()")
        return "STATE"

    def  __str__(self):
        print(f"{self.__dict__ = }")


def create_fee_side(name: str, content: dict):
    print(f"{name = }, {content = }")

    if name.startswith("int_enum//"):
        name = name[10:]

    definition = {}
    for side_name, side_definition in content.items():
        aliases = side_definition["alias"]
        value = side_definition["value"]

        definition[side_name] = value

        for alias in aliases:
            definition[alias] = value
    return FEE_SIDE(name, definition)


@pytest.mark.xfail(raises=pickle.PicklingError)
def test_pickle_loads():

    print()

    x = create_fee_side('FEE_SIDE', {'E': {'alias': 'e', 'value': 1}, 'F': {'alias': 'f', 'value': 2}})
    print(f"{vars(x) = }")
    print(f"{dir(x) = }")
    print(f"{x = }")

    assert hasattr(x, "__getstate__")
    assert hasattr(x, "__setstate__")

    y = pickle.dumps(x)
    print(f"{y = }")
