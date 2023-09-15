import shutil
from pathlib import Path

import pytest

from egse.config import find_dirs
from egse.config import find_file
from egse.config import find_files
from egse.config import find_first_occurrence_of_dir
from egse.config import find_root
from egse.config import get_common_egse_root
from egse.config import get_resource_dirs
from egse.config import get_resource_path

HERE = Path(__file__).parent.resolve()


def test_get_resource_dirs():

    assert len(get_resource_dirs()) > 0


def test_get_resource_path():

    with pytest.raises(FileNotFoundError):
        get_resource_path("non-existing-file")

    # The following resources should all exist in this project
    # We don't need the return value as the function raises a FileNotFoundError
    # when the resource is not found.

    _ = get_resource_path(
        "empty_data_file.txt", Path(__file__).parent
    )  # in ./tests/data, i.e. <project root>/src/tests/data
    _ = get_resource_path("home.svg")  # in <project root>src/egse/images
    _ = get_resource_path("symetrie_logo.png")  # in <project root>/images


def test_find_first_occurrence_of_dir():

    assert str(find_first_occurrence_of_dir("conf", root=HERE)).endswith("tests/data/conf")
    assert str(find_first_occurrence_of_dir("CSL/conf", root=HERE)).endswith("tests/data/CSL/conf")

    assert find_first_occurrence_of_dir("not-a-directory", root=HERE) is None

    assert str(find_first_occurrence_of_dir("/egse/images")).endswith("src/egse/images")

    folders = (
        HERE / "x_data/01/kul",
        HERE / "x_data/02/kul",
        HERE / "x_data/02/42/kul",
        HERE / "x_data/03/42/kul",
        HERE / "x_data/03/43/kul",
        HERE / "x_data/03/43/kul/ivs",
        HERE / "x_data/04/42/kal",
        HERE / "x_data/04/42/kul",
    )
    for folder in folders:
        folder.mkdir(parents=True)

    assert str(find_first_occurrence_of_dir("kul", root=HERE)).endswith("tests/x_data/01/kul")
    assert str(find_first_occurrence_of_dir("03/42/kul", root=HERE)).endswith("tests/x_data/03/42/kul")
    assert str(find_first_occurrence_of_dir("03/*/kul", root=HERE)).endswith("tests/x_data/03/42/kul")
    assert str(find_first_occurrence_of_dir("42/kul", root=HERE)).endswith("tests/x_data/02/42/kul")
    assert str(find_first_occurrence_of_dir("*/42/kul", root=HERE)).endswith("tests/x_data/02/42/kul")
    assert str(find_first_occurrence_of_dir("ivs", root=HERE)).endswith("tests/x_data/03/43/kul/ivs")
    assert str(find_first_occurrence_of_dir("04/*/k?l", root=HERE)).endswith("tests/x_data/04/42/kal")

    shutil.rmtree(HERE / "x_data")


def test_find_root():

    assert find_root(None) is None
    assert find_root("/") is None
    assert find_root("/", tests=("tmp",)) == Path("/")
    assert find_root("/", tests=("non-existing-tmp",)) is None


def test_get_common_egse_root():

    # for the following test I assume that we are in the repository, but we can not test
    # the value as it will be different for each installation
    assert get_common_egse_root() is not None

    # for the following test I assume that we are on a unix system (Linux or macOS)
    assert get_common_egse_root(Path("/tmp")) is None


def test_find_root_exceptions():

    assert find_root("/non-existing-path") is None
    assert find_root(None) is None


def test_get_common_egse_root_with_env():

    import os

    os.environ["PLATO_COMMON_EGSE_PATH"] = "/Users/rik/git"

    # I added lru_cache to speed up the get_common_egse_root() function, but this
    # is of course fatal for test harnesses. Therefore, clear the cache before and
    # after this test.

    get_common_egse_root.cache_clear()

    assert get_common_egse_root() == Path("/Users/rik/git")

    get_common_egse_root.cache_clear()

    del os.environ["PLATO_COMMON_EGSE_PATH"]


def test_find_files():
    files = list(find_files("COPY*", root=get_common_egse_root()))
    assert files

    for f in files:
        assert f.name.startswith("COPY")

    # no files named 'data', only folders that are named 'data', use find_dirs for this.

    files = list(find_files("data", root=get_common_egse_root() / "src"))
    assert not files

    # When I want to find a file in a specific directory, use the in_dir keyword

    filename = Path("EtherSpaceLink_v*.dylib")
    files = list(find_files(filename, in_dir="lib/CentOS-7"))
    print()
    print(files)

    # The expected file is in the src/egse/lib/CentOS-7 folder, but
    # there could also be a build directory which contains the file.

    assert len(files) in (1, 2)


def test_find_dirs():
    dir_name = "CentOS-[78]"
    dirs = list(find_dirs(dir_name))
    assert dirs

    dir_name = "CentOS-7"
    dirs = list(find_dirs(dir_name))
    assert dirs

    dir_name = "egse/images"
    dirs = list(find_dirs(dir_name))
    print(dirs)
    # The third file could be in the build folder which doesn't always exists.
    # A fourth file could be in the virtual environment venv or venv38
    assert len(dirs) in (2, 3, 4)

    # use the leading '/' to prevent that 'plato-common-egse/images' is matched.

    dir_name = "/egse/images"
    dirs = list(find_dirs(dir_name))
    print(dirs)
    # The second file could be in the build folder which doesn't always exists.
    assert len(dirs) in (1, 2)


def test_find_file():

    assert find_file("COPY*")
    assert find_file("empty_data_file.txt")
    assert not find_file("non-existing-file.txt")

    assert find_file("__init__.py", in_dir="egse")
