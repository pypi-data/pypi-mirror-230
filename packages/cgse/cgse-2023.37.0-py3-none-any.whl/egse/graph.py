"""
The graph module defines classes and functions to work with graphs.

This code is taken and adapted from the book:

    Classic Computer Science Problems in Python, David Kopec, 2019.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Generic, TypeVar, List

V = TypeVar('V')  # type of the vertices in the graph


@dataclass
class Edge:
    """
    An Edge defines the connection between two vertices.
    Each vertex is represented by an integer index. By convention,
    `u` refers to the first, i.e. 'from', vertex and `v` represents the
    second, i.e. 'to', vertex. By this definition, an Edge is directed
    from vertex 'u' to vertex 'v'.
    """
    u: int  # the 'from' vertex
    v: int  # the 'to' vertex

    def reversed(self) -> Edge:
        """Returns the reverse connection of this Edge."""
        return Edge(self.v, self.u)

    def __str__(self) -> str:
        return f"{self.u} -> {self.v}"


class Graph(Generic[V]):
    def __init__(self, vertices: List[V] = None) -> None:
        if vertices is None:
            vertices = []
        self._vertices: List[V] = vertices
        self._edges: List[List[Edge]] = [[] for _ in vertices]

    @property
    def vertex_count(self) -> int:
        """Returns the number of vertices."""
        return len(self._vertices)

    @property
    def edge_count(self) -> int:
        """Returns the number of edges."""
        return sum(map(len, self._edges))

    def add_vertex(self, vertex: V) -> int:
        """Adds a vertex to the graph and returns its index."""
        self._vertices.append(vertex)
        self._edges.append([])
        return self.vertex_count - 1

    def add_edge(self, edge: Edge) -> None:
        """
        Add a edge to the graph. Since this is an undirected graph,
        we always add edges in both directions.
        """
        self._edges[edge.u].append(edge)
        self._edges[edge.v].append(edge.reversed())

    def add_edge_by_index(self, u: int, v: int) -> None:
        """
        Convenience method to add an edge by index.

        Args:
            u (int): the index of the 'from' vertex
            v (int): the index of the 'to' vertex
        """
        edge: Edge = Edge(u, v)
        self.add_edge(edge)

    def add_edge_by_vertices(self, first: V, second: V) -> None:
        """
        Convenience method to add an edge by looking up Vertex indices.

        Args:
            first (V): the first 'from' vertex
            second (V): the second 'to' vertex
        """
        u: int = self._vertices.index(first)
        v: int = self._vertices.index(second)
        self.add_edge_by_index(u, v)

    def vertex_at(self, index: int) -> V:
        """Finds the vertex at a specific index."""
        return self._vertices[index]

    def index_of(self, vertex: V) -> int:
        """Finds the index of a vertex in the graph."""
        return self._vertices.index(vertex)

    def neighbors_for_index(self, index: int) -> List[V]:
        """Returns all the vertices that a vertex at a specific index is connected to."""
        return [self.vertex_at(e.v) for e in self._edges[index]]

    def neighbors_for_vertex(self, vertex: V) -> List[V]:
        """Returns all the vertices that the given vertex is connected to."""
        return self.neighbors_for_index(self.index_of(vertex))

    def edges_for_index(self, index: int) -> List[Edge]:
        """Returns all the edges that are associated with a vertex at the given index."""
        return self._edges[index]

    def edges_for_vertex(self, vertex: V) -> List[Edge]:
        """Returns all the edges that are associated with the given vertex."""
        return self.edges_for_index(self.index_of(vertex))

    def __str__(self) -> str:
        desc: str = ""
        for idx in range(self.vertex_count):
            desc += f"{self.vertex_at(idx)} -> {self.neighbors_for_index(idx)}\n"
        return desc


# The Graph implementation is that of an undirected graph

UndirectedGraph = Graph


class DirectedGraph(Graph):
    def add_edge(self, edge: Edge) -> None:
        """
        Add a edge to the graph. Since this is an directed graph, we add just this edge to the graph.
        """
        self._edges[edge.u].append(edge)


