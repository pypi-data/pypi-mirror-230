"""
This test demonstrates how a fixture can be LRU cached.

The idea is that such a fixture contains a time consuming check for a device. For some devices
it takes several seconds to timeout the connect() method when a device is not connected.
We then usually use a simulator to run the same tests when the device is not available, but if the
fixture would run for each test method, it would take minutes to run the test because the same
check is done again and again.

When you run this test, you will see that the simple fixture is executed for every test method
while the cached fixture only runs once.
"""

from functools import lru_cache

import pytest


@pytest.fixture
def simple_fixture():
    print("executing simple fixture")
    return "A simple fixture result"


@pytest.fixture
@lru_cache
def cached_fixture():
    print("executing cached fixture")
    return "A cached fixture result"


def test_simple_str_fixture_1(simple_fixture):

    assert "simple" in simple_fixture


def test_simple_str_fixture_2(simple_fixture):

    assert "simple" in simple_fixture


def test_simple_str_fixture_3(simple_fixture):

    assert "simple" in simple_fixture


def test_fixture_caching_1(cached_fixture):

    assert "cached" in cached_fixture


def test_fixture_caching_2(cached_fixture):

    assert "cached" in cached_fixture


def test_fixture_caching_3(cached_fixture):

    assert "cached" in cached_fixture
