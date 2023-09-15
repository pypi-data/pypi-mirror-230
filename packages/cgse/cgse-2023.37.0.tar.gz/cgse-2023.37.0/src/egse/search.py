"""
The search module defines some generic search functions.

This code is taken from the book:

    Classic Computer Science Problems in Python, David Kopec, 2019.
"""
from __future__ import annotations

from collections import deque
from typing import TypeVar, Iterable, Sequence, Generic, List, \
    Callable, Set, Deque, Dict, Any, Optional
from typing_extensions import Protocol
from heapq import heappush, heappop

T = TypeVar('T')


def linear_contains(iterable: Iterable[T], key: T) -> bool:
    for item in iterable:
        if item == key:
            return True
    return False


# Note that Protocol is used here to define the Comparable type with structural
# sub-typing. A Comparable type implements the comparison operators.
# Protocol is defined in PEP-544 [https://www.python.org/dev/peps/pep-0544/]

C = TypeVar('C', bound='Comparable')


class Comparable(Protocol):
    def __eq__(self, other: Any) -> bool:
        ...

    def __lt__(self: C, other: C) -> bool:
        ...

    def __gt__(self: C, other: C) -> bool:
        return (not self < other) and self != other

    def __le__(self: C, other: C) -> bool:
        return self < other or self == other

    def __ge__(self: C, other: C) -> bool:
        return not self < other


def binary_contains(sequence: Sequence[C], key: C) -> bool:
    low: int = 0
    high: int = len(sequence) - 1
    while low <= high:  # while there is still a search space
        mid: int = (low + high) // 2
        if sequence[mid] < key:
            low = mid + 1
        elif sequence[mid] > key:
            high = mid - 1
        else:
            return True
    return False


class Stack(Generic[T]):
    def __init__(self) -> None:
        self._container: List[T] = []

    @property
    def empty(self) -> bool:
        return not self._container

    def push(self, item: T) -> None:
        self._container.append(item)

    def pop(self) -> T:
        return self._container.pop()  # LIFO

    def __repr__(self) -> str:
        return repr(self._container)


class Node(Generic[T]):
    def __init__(self, state: T, parent: Optional[Node], cost: float = 0.0, heuristic: float = 0.0) -> None:
        self.state: T = state
        self.parent: Optional[Node] = parent
        self.cost: float = cost
        self.heuristic: float = heuristic

    def __lt__(self, other: Node) -> bool:
        return (self.cost + self.heuristic) < (other.cost + other.heuristic)


def depth_first_search(initial: T, goal_test: Callable[[T], bool], successors: Callable[[T], List[T]]) -> Optional[Node[T]]:
    """
    The depth-first search (DFS) algorithm goes as deeply as it can before backtracking to its
    last decision point if it reaches a dead end.

    Args:
        initial: starting point for the search
        goal_test: function that defines if the goal is reached or not
        successors: function that returns all possible states that can be visited next

    Returns:
        the Node encapsulating the goal state if successful, otherwise None.
    """
    frontier: Stack[Node[T]] = Stack()
    frontier.push(Node(initial, None))
    explored: Set[T] = set(initial)

    while not frontier.empty:
        current_node: Node[T] = frontier.pop()
        current_state: T = current_node.state

        if goal_test(current_state):
            return current_node

        for child in successors(current_state):
            if child in explored:
                continue
            explored.add(child)
            frontier.push(Node(child, current_node))

    return None  # we went through everything and never found goal


def node_to_path(node: Node[T]) -> List[T]:
    """
    Returns the path that was followed from a starting state to reach a goal.

    Args:
        node:

    Returns:
        a list of states that were visited to reach the final goal.
    """
    path: List[T] = [node.state]

    while node.parent is not None:
        node = node.parent
        path.append(node.state)
    path.reverse()
    return path


class Queue(Generic[T]):
    def __init__(self) -> None:
        self._container: Deque[T] = deque()

    @property
    def empty(self) -> bool:
        return not self._container

    def push(self, item: T) -> None:
        self._container.append(item)

    def pop(self) -> T:
        return self._container.popleft()

    def __repr__(self) -> str:
        return repr(self._container)


def breadth_first_search(initial: T, goal_test: Callable[[T], bool], successors: Callable[[T], List[T]]) -> Optional[Node[T]]:
    frontier: Queue[Node[T]] = Queue()
    frontier.push(Node(initial, None))
    explored: Set[T] = set(initial)

    while not frontier.empty:
        current_node: Node[T] = frontier.pop()
        current_state: T = current_node.state

        if goal_test(current_state):
            return current_node

        for child in successors(current_state):
            if child in explored:
                continue
            explored.add(child)
            frontier.push(Node(child, current_node))

    return None  # we went through everything and never found goal

