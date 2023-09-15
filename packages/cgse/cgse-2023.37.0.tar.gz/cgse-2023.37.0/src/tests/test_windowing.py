from random import randrange, getrandbits, sample
import numpy as np
import pytest

from egse.windowing import WindowSizeError, WindowList, CCDIndexError, extract_window_data
from egse.decorators import timer


def generate_sample_image(nrows, ncols):

    image = np.zeros((nrows, ncols), dtype=np.int32)

    for idx_x in range(nrows):
        for idx_y in range(ncols):
            image[idx_x][idx_y] = idx_x * 100 + idx_y

    return image


def test_window_list_creation_empty():

    wl = WindowList()

    with pytest.raises(CCDIndexError):
        assert wl.get_window_count(0) == 0
    assert wl.get_window_count(1) == 0
    assert wl.get_window_count(2) == 0
    assert wl.get_window_count(3) == 0
    assert wl.get_window_count(4) == 0


def test_window_list_adding():

    wl = WindowList()

    with pytest.raises(CCDIndexError):
        wl.add_window(0, 0, 0, 0)

    wl.add_window(0, 0, 0, 1)
    wl.add_window(10, 10, 0, 3)

    assert wl.get_window_count(ccd_nr=1) == 1
    assert wl.get_window_count(ccd_nr=2) == 0
    assert wl.get_window_count(ccd_nr=3) == 1
    assert wl.get_window_count(ccd_nr=4) == 0


def test_window_list_access():

    window_list = WindowList()

    ccd_1 = [
        [0, 0, 0],
        [10, 10, 0],
        [20, 20, 0],
        [30, 30, 0],
        [40, 40, 0],
        [50, 50, 0],
        [60, 60, 0],
        [70, 70, 0],
        [80, 80, 0],
        [90, 90, 0],
    ]

    for window in ccd_1:
        window_list.add_window(window[0], window[1], window[2], 1)

    assert window_list.get_window_count(1) == 10

    with pytest.raises(CCDIndexError):
        window_list.get_window_list_for_ccd(0)


def test_window_list_sorted():

    window_list = WindowList()

    wl = [
        (0, 0, 0),
        (10, 10, 0),
        (20, 10, 0),
        (15, 30, 0),
        (30, 30, 0),
        (50, 30, 0),
        (60, 60, 0),
        (70, 70, 0),
        (80, 80, 0),
        (90, 90, 0),
    ]

    for window in sample(wl, k=len(wl)):
        window_list.add_window(window[0], window[1], window[2], 1)

    for window in sample(wl, k=len(wl)):
        window_list.add_window(window[0], window[1], window[2], 2)

    for window in sample(wl, k=len(wl)):
        window_list.add_window(window[0], window[1], window[2], 3)

    for window in sample(wl, k=len(wl)):
        window_list.add_window(window[0], window[1], window[2], 4)

    print(window_list)

    assert window_list.get_window_list_for_ccd(1) == wl
    assert window_list.get_window_list_for_ccd(2) == wl
    assert window_list.get_window_list_for_ccd(3) == wl
    assert window_list.get_window_list_for_ccd(4) == wl


def test_window_size_exceptions():
    window_list = WindowList()

    window_list.set_window_size(2, 2)
    window_list.set_window_size(32, 32)

    with pytest.raises(WindowSizeError):
        window_list.set_window_size(1, 10)

    with pytest.raises(WindowSizeError):
        window_list.set_window_size(33, 10)

    with pytest.raises(WindowSizeError):
        window_list.set_window_size(10, 1)

    with pytest.raises(WindowSizeError):
        window_list.set_window_size(10, 33)


def test_window_list_sorted_large():

    window_list = WindowList()

    ccd_1r = [[randrange(0, 4000, 1), randrange(0, 4000, 1), getrandbits(1)] for _ in range(100000)]
    ccd_2r = [[randrange(0, 4000, 1), randrange(0, 4000, 1), getrandbits(1)] for _ in range(100000)]
    ccd_3r = [[randrange(0, 4000, 1), randrange(0, 4000, 1), getrandbits(1)] for _ in range(100000)]
    ccd_4r = [[randrange(0, 4000, 1), randrange(0, 4000, 1), getrandbits(1)] for _ in range(100000)]

    for window in ccd_1r:
        window_list.add_window(window[0], window[1], window[2], 1)
    for window in ccd_2r:
        window_list.add_window(window[0], window[1], window[2], 2)
    for window in ccd_3r:
        window_list.add_window(window[0], window[1], window[2], 3)
    for window in ccd_4r:
        window_list.add_window(window[0], window[1], window[2], 4)

    wl_1 = window_list.get_window_list_for_ccd(1)
    wl_2 = window_list.get_window_list_for_ccd(2)
    wl_3 = window_list.get_window_list_for_ccd(3)
    wl_4 = window_list.get_window_list_for_ccd(4)

    print(window_list)


def test_extract_window_data():

    wl = WindowList()

    wl.set_window_size(5, 3)
    wl.add_window(0, 0, 0, 1)
    wl.add_window(0, 0, 1, 1)
    wl.add_window(4, 2, 0, 1)

    x_size, y_size = wl.get_window_size()

    image = generate_sample_image(20, 20)
    print(image)

    windows = wl.get_window_list_for_ccd(1)

    window = windows[0]
    imagette = extract_window_data(image, window[0], window[1], x_size, y_size, window[2])

    assert imagette.shape == (3, 5)  # x = cols, y = rows
    assert imagette[0][0] == 0
    assert imagette[0][4] == 4
    assert imagette[2][0] == 200
    assert imagette[2][4] == 204

    window = windows[1]
    imagette = extract_window_data(image, window[0], window[1], x_size, y_size, window[2])

    assert imagette.shape == (3, 5)  # x = cols, y = rows
    assert imagette[0][0] == 15
    assert imagette[0][4] == 19
    assert imagette[2][0] == 215
    assert imagette[2][4] == 219

    window = windows[2]
    imagette = extract_window_data(image, window[0], window[1], x_size, y_size, window[2])

    assert imagette.shape == (3, 5)  # x = cols, y = rows
    assert imagette[0][0] == 204
    assert imagette[0][4] == 208
    assert imagette[2][0] == 404
    assert imagette[2][4] == 408


def test_extract_window_data_exception():

    with pytest.raises(ValueError):
        image = generate_sample_image(20, 20)
        imagette = extract_window_data(image, 0, 0, 10, 10, 2)

    # Remember slicing doesn't raise any exceptions when out-of-bounds,
    # but instead returns cropped or empty arrays

    imagette = extract_window_data(image, 10, 10, 30, 30, 0)
    assert imagette.shape == (10, 10)

    imagette = extract_window_data(image, 20, 20, 10, 10, 0)
    assert imagette.shape == (0, 0)
