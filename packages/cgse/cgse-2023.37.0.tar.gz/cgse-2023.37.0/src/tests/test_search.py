import pytest

from egse.search import linear_contains, binary_contains, Stack


def test_linear_contains():
    assert linear_contains([1, 5, 15, 15, 15, 15, 25], 5)
    assert not linear_contains([1, 5, 15, 15, 15, 15, 25], 13)
    assert linear_contains(('a', 'b', 'c', 'd'), 'c')
    assert not linear_contains(('a', 'b', 'c', 'd'), 'e')


def test_binary_contains():
    assert binary_contains([1, 5, 15, 15, 15, 15, 25], 5)
    assert not binary_contains([1, 5, 15, 15, 15, 15, 25], 13)
    assert binary_contains(('a', 'b', 'c', 'd'), 'c')
    assert not binary_contains(('a', 'b', 'c', 'd'), 'e')


def test_stack():
    stack = Stack()

    assert stack.empty

    with pytest.raises(IndexError):
        assert stack.pop()

    stack.push("first element")

    assert not stack.empty
    assert stack.pop() == 'first element'
    assert stack.empty

    stack.push("1")
    stack.push(2)
    stack.push((4, 2))

    assert stack.pop() == (4, 2)
    assert stack.pop() == 2
    assert stack.pop() == "1"
