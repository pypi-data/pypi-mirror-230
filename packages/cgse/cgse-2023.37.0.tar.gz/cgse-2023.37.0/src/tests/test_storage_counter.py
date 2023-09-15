import shutil
from pathlib import Path

from egse.storage import _read_counter
from egse.storage import _write_counter
from egse.storage import determine_counter_from_dir_list
from egse.storage import get_counter
from egse.system import chdir

THIS_FILE_LOCATION = Path(__file__).parent
NUM_FILES = 100


def test_read_counter_on_empty_dir():

    test_dir = Path(THIS_FILE_LOCATION / "counter_test")

    test_dir.mkdir(exist_ok=True)

    file_path = Path("test_counter.count")

    with chdir(test_dir):
        counter = _read_counter(file_path)
        assert counter == 0

    shutil.rmtree(test_dir)


def test_write_counter_on_empty_dir():

    test_dir = Path(THIS_FILE_LOCATION / "counter_test")

    test_dir.mkdir(exist_ok=True)

    file_path = Path("test_counter.count")

    with chdir(test_dir):
        _write_counter(23, file_path)
        counter = _read_counter(file_path)
        assert counter == 23

    shutil.rmtree(test_dir)


def test_read_counter_on_existing_dir():

    test_dir = Path(THIS_FILE_LOCATION / "counter_test")

    test_dir.mkdir(exist_ok=True)

    file_path = Path("test_counter.count")

    with chdir(test_dir):
        _write_counter(42, file_path)

    with chdir(test_dir):
        counter = _read_counter(file_path)
        assert counter == 42

    shutil.rmtree(test_dir)


def test_get_counter_on_empty_dir():

    test_dir = Path(THIS_FILE_LOCATION / "counter_test")

    test_dir.mkdir(exist_ok=True)

    file_path = Path("test_counter.count")

    with chdir(test_dir):
        counter = get_counter(file_path)
        assert counter == 1

    shutil.rmtree(test_dir)


def test_get_counter_on_existing_files():

    test_dir = Path(THIS_FILE_LOCATION / "counter_test")

    test_dir.mkdir(exist_ok=True)

    file_path = Path("test_counter.count")

    with chdir(test_dir):
        for i in range(1, NUM_FILES + 1):
            Path(f"TEST_{i:06d}_XXX.ext").touch()

        counter = determine_counter_from_dir_list(test_dir, "TEST_*.ext", index=-2)

        _write_counter(counter, file_path)
        assert counter == NUM_FILES + 1

        counter = get_counter(file_path)
        assert counter == NUM_FILES + 2

    shutil.rmtree(test_dir)
