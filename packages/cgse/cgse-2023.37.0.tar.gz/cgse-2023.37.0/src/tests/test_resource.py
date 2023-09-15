import shutil
from pathlib import Path

import pytest

from egse.resource import AmbiguityError
from egse.resource import NoSuchFileError
from egse.resource import add_resource_id
from egse.resource import get_resource
from egse.resource import get_resource_locations
from egse.resource import initialise_resources

HERE = Path(__file__).parent.resolve()


@pytest.fixture
def reset_resource():
    import egse.resource
    egse.resource.__initialised__ = False


def test_initialisation(caplog):

    # The resource module initialises itself with root=__file__

    _ = get_resource(":/icons/open-document-hdf5.png")

    # This will just issue a warning log message

    initialise_resources()

    assert "already been initialised" in caplog.text


def test_initialisation_ambiguity(reset_resource):

    # Let's first create a directory hierarchy that contains ambiguity in the sense that the same folder
    # exists at different levels in the hierarchy. `data` is a default resource location and we will use
    # that for this test.

    folders = (
            HERE / "x_resources" / "aaa" / "xdata",
            HERE / "x_resources" / "xxx" / "data",
            HERE / "x_resources" / "xxx" / "one" / "data",
            HERE / "x_resources" / "xxx" / "two" / "data",
            HERE / "x_resources" / "bbb" / "one" / "data",
    )

    for folder in folders:
        folder.mkdir(parents=True, exist_ok=True)

    # This function should not raise an AmbiguityError anymore

    initialise_resources(HERE / "x_resources")

    resource_locations = get_resource_locations()

    assert resource_locations['data'].match("*/x_resources/bbb/one/data")

    shutil.rmtree(HERE / "x_resources")


def test_get_resource(reset_resource):

    # Need to call initialise here because we reset the module in the fixture

    initialise_resources()

    pathname = get_resource(":/icons/open-document-hdf5.png")
    assert isinstance(pathname, Path)
    assert "document" in str(pathname)
    assert pathname.exists()

    pathname = get_resource(":/images/home.svg")
    assert isinstance(pathname, Path)
    assert "home" in str(pathname)
    assert pathname.exists()

    with pytest.raises(NoSuchFileError):
        _ = get_resource(":/icons/no-such-file.png")

    pathname = get_resource(__file__)
    assert isinstance(pathname, Path)
    assert "resource" in str(pathname)
    assert pathname.exists()

    with pytest.raises(NoSuchFileError):
        _ = get_resource("resource.py")

    pathname = get_resource(":/lib/macOS/EtherSpaceLink_v34_86.dylib")
    assert isinstance(pathname, Path)
    assert "macOS" in str(pathname)
    assert pathname.exists()

    # The following raise the exception because there are three such files in the system

    with pytest.raises(AmbiguityError):
        _ = get_resource(":/lib/*/EtherSpaceLink_v34_86.dylib")

    with pytest.raises(NotImplementedError):
        _ = get_resource(":/lib/**/EtherSpaceLink_v34_86.dylib")


def test_get_resource_with_wildcard(reset_resource):

    initialise_resources()
    add_resource_id("RCs", Path(__file__).parent / "data/resources")

    rc_file = get_resource(":/RCs/001_*.txt")

    assert "RC2" in str(rc_file)

    with pytest.raises(AmbiguityError):
        _ = get_resource(":/RCs/*_20220906_*.txt")

    with pytest.raises(AmbiguityError):
        _ = get_resource(":/RCs/00?_20220906_*.txt")

    with pytest.raises(NoSuchFileError):
        _ = get_resource(":/RCs/00?_2021*.txt")


def test_add_resource(reset_resource):

    # Need to call initialise here because we reset the module in the fixture

    initialise_resources()

    resources = get_resource_locations()

    assert 'icons' in resources
    assert 'images' in resources
    assert 'lib' in resources

    with pytest.raises(ValueError):
        add_resource_id("lib", "lib")

    add_resource_id("lib", "lib", force=True)

    with pytest.raises(ValueError):
        add_resource_id("styles", "xxx")

    add_resource_id("styles", "/Users/rik/git/plato-common-egse/src/egse", force=True)

    assert "styles" in get_resource_locations()
