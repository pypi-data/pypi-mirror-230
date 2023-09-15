import logging
import pytest
from typing import List, Optional
from egse.graph import Edge, Graph, V, DirectedGraph
from egse.search import Node, breadth_first_search, node_to_path, depth_first_search


def create_undirected_graph(nodes: List[V], edges: List[tuple]):
    graph = Graph()

    for node in nodes:
        graph.add_vertex(node)

    for vertex_from, vertex_to in edges:
        u: int = graph.index_of(vertex_from)
        v: int = graph.index_of(vertex_to)
        graph.add_edge(Edge(u, v))

    return graph


def create_directed_graph():
    graph = DirectedGraph(['A1', 'A2', 'A3', 'A4', 'B1', 'B2', 'B3', 'B4'])

    graph.add_edge_by_vertices('A1', 'A2')
    graph.add_edge_by_vertices('A2', 'A3')
    graph.add_edge_by_vertices('A3', 'A4')
    graph.add_edge_by_vertices('A4', 'B1')
    graph.add_edge_by_vertices('B1', 'B2')
    graph.add_edge_by_vertices('B2', 'B3')
    graph.add_edge_by_vertices('B1', 'B4')

    return graph


def create_msa_graph():
    graph = Graph(
        ["Seattle", "San Fransisco", "Los Angeles", "Riverside", "Phoenix", "Chicago",
         "Boston", "New York", "Atlanta", "Miami", "Dallas", "Houston", "Detroit",
         "Philadelphia", "Washington"]
    )
    graph.add_edge_by_vertices("Seattle", "Chicago")
    graph.add_edge_by_vertices("Seattle", "San Fransisco")
    graph.add_edge_by_vertices("San Fransisco", "Riverside")
    graph.add_edge_by_vertices("San Fransisco", "Los Angeles")
    graph.add_edge_by_vertices("Los Angeles", "Riverside")
    graph.add_edge_by_vertices("Los Angeles", "Phoenix")
    graph.add_edge_by_vertices("Riverside", "Phoenix")
    graph.add_edge_by_vertices("Riverside", "Chicago")
    graph.add_edge_by_vertices("Phoenix", "Dallas")
    graph.add_edge_by_vertices("Phoenix", "Houston")
    graph.add_edge_by_vertices("Dallas", "Chicago")
    graph.add_edge_by_vertices("Dallas", "Atlanta")
    graph.add_edge_by_vertices("Dallas", "Houston")
    graph.add_edge_by_vertices("Houston", "Atlanta")
    graph.add_edge_by_vertices("Houston", "Miami")
    graph.add_edge_by_vertices("Atlanta", "Chicago")
    graph.add_edge_by_vertices("Atlanta", "Washington")
    graph.add_edge_by_vertices("Atlanta", "Miami")
    graph.add_edge_by_vertices("Miami", "Washington")
    graph.add_edge_by_vertices("Chicago", "Detroit")
    graph.add_edge_by_vertices("Detroit", "Boston")
    graph.add_edge_by_vertices("Detroit", "Washington")
    graph.add_edge_by_vertices("Detroit", "New York")
    graph.add_edge_by_vertices("Boston", "New York")
    graph.add_edge_by_vertices("New York", "Philadelphia")
    graph.add_edge_by_vertices("Philadelphia", "Washington")

    return graph


def test_graph_creation():
    graph = create_undirected_graph(
        ['A1', 'A2', 'A3', 'B1', 'B2', 'B3'],
        [('A1', 'A2'), ('A1', 'A3'), ('A3', 'B1'), ('B1', 'B2'), ('B1', 'B3')]
    )

    assert graph.neighbors_for_vertex('A1') == ['A2', 'A3']
    assert graph.neighbors_for_vertex('B1') == ['A3', 'B2', 'B3']


def test_graph_str():
    graph = create_undirected_graph(['A1', 'A2'], [('A1', 'A2')])
    output = str(graph)

    assert "A1 -> ['A2']" in output
    assert "A2 -> ['A1']" in output


def test_edge_str():
    edge = Edge(0, 1)
    output = str(edge)

    assert output == "0 -> 1"


def test_edge_constructor():
    edge = Edge(0, 1)
    assert edge.reversed() == Edge(1, 0)
    assert edge.reversed() != edge
    assert edge.reversed() != Edge(0, 1)


def test_graph_constructor():
    graph = Graph(['A1', 'A2', 'A3', 'A4', 'A5'])
    assert graph.vertex_count == 5
    assert graph.edge_count == 0

    assert graph.vertex_at(0) == 'A1'
    assert graph.vertex_at(1) == 'A2'
    assert graph.vertex_at(2) == 'A3'
    assert graph.vertex_at(3) == 'A4'
    assert graph.vertex_at(4) == 'A5'

    assert graph.index_of('A1') == 0
    assert graph.index_of('A2') == 1
    assert graph.index_of('A3') == 2
    assert graph.index_of('A4') == 3
    assert graph.index_of('A5') == 4


def test_add_vertex():

    graph = Graph(['A1', 'A2', 'A3', 'A4', 'A5'])

    b1 = graph.add_vertex('B1')
    assert graph.vertex_count == 6

    b2 = graph.add_vertex('B2')
    b3 = graph.add_vertex('B3')
    b4 = graph.add_vertex('B4')
    b5 = graph.add_vertex('B5')
    assert graph.vertex_count == 10

    for idx in range(graph.vertex_count):
        assert not graph.neighbors_for_index(idx)


def test_add_edge():

    graph = Graph(['A1', 'A2', 'A3', 'A4', 'A5',
                   'B1', 'B2', 'B3', 'B4', 'B5',])

    edge = Edge(graph.index_of('A1'), graph.index_of('B1'))
    graph.add_edge(edge)
    edge = Edge(graph.index_of('A2'), graph.index_of('B2'))
    graph.add_edge(edge)
    edge = Edge(graph.index_of('A3'), graph.index_of('B3'))
    graph.add_edge(edge)
    edge = Edge(graph.index_of('A4'), graph.index_of('B5'))
    graph.add_edge(edge)
    edge = Edge(graph.index_of('A5'), graph.index_of('B4'))
    graph.add_edge(edge)


def test_add_edge_by_index():

    graph = Graph(['A1', 'A2', 'A3', 'B1', 'B2', 'B3'])

    graph.add_edge_by_index(graph.index_of('A1'), graph.index_of('B1'))
    graph.add_edge_by_index(graph.index_of('A2'), graph.index_of('B2'))
    graph.add_edge_by_index(graph.index_of('A3'), graph.index_of('B3'))
    graph.add_edge_by_index(graph.index_of('B3'), graph.index_of('A2'))
    graph.add_edge_by_index(graph.index_of('B2'), graph.index_of('A1'))
    graph.add_edge_by_index(graph.index_of('B3'), graph.index_of('A1'))

    assert graph.neighbors_for_vertex('A1') == ['B1', 'B2', 'B3']
    assert len(graph.neighbors_for_vertex('B3')) == 3
    assert 'A3' in graph.neighbors_for_vertex('B3')
    assert 'A2' in graph.neighbors_for_vertex('B3')
    assert 'A1' in graph.neighbors_for_vertex('B3')


def test_add_edge_by_vertices():

    graph = Graph(['A1', 'A2', 'A3', 'B1', 'B2', 'B3'])

    graph.add_edge_by_vertices('A1', 'B1')
    graph.add_edge_by_vertices('A2', 'B2')
    graph.add_edge_by_vertices('A3', 'B3')
    graph.add_edge_by_vertices('B3', 'A2')
    graph.add_edge_by_vertices('B2', 'A1')
    graph.add_edge_by_vertices('B3', 'A1')

    assert graph.neighbors_for_vertex('A1') == ['B1', 'B2', 'B3']
    assert len(graph.neighbors_for_vertex('B3')) == 3
    assert 'A3' in graph.neighbors_for_vertex('B3')
    assert 'A2' in graph.neighbors_for_vertex('B3')
    assert 'A1' in graph.neighbors_for_vertex('B3')


def test_dfs():
    """Test the Depth-First Search algorithm for the city graph."""
    graph = create_msa_graph()

    dfs_result: Optional[Node[V]] = depth_first_search("Boston", lambda x: x == "Miami", graph.neighbors_for_vertex)

    assert dfs_result is not None

    path: List[V] = node_to_path(dfs_result)

    assert path == ['Boston', 'New York', 'Philadelphia', 'Washington', 'Miami']


def test_bfs():
    """Test the Breadth-First Search algorithm for the city graph. This will give the shortest distance."""
    graph = create_msa_graph()

    bfs_result: Optional[Node[V]] = breadth_first_search("Boston", lambda x: x == "Miami", graph.neighbors_for_vertex)

    assert bfs_result is not None

    path: List[V] = node_to_path(bfs_result)

    assert path == ['Boston', 'Detroit', 'Washington', 'Miami']


def test_undirected_graph():
    graph = create_undirected_graph(
        ['A1', 'A2', 'A3', 'A4', 'B1', 'B2', 'B3', 'B4'],
        [('A1', 'A2'), ('A2', 'A3'), ('A3', 'A4'), ('A4', 'B1'), ('B1', 'B2'), ('B2', 'B3'), ('B1', 'B4')])

    assert graph.vertex_count == 8
    assert graph.edge_count == 14

    assert graph.neighbors_for_vertex('B1') == ['A4', 'B2', 'B4']
    assert len(graph.edges_for_vertex('B1')) == 3

    dfs_result = depth_first_search('A1', lambda x: x == 'B3', graph.neighbors_for_vertex)
    assert dfs_result is not None

    dfs_path: List[V] = node_to_path(dfs_result)

    bfs_result = breadth_first_search('A1', lambda x: x == 'B3', graph.neighbors_for_vertex)
    assert bfs_result is not None

    bfs_path: List[V] = node_to_path(bfs_result)

    # For this particular directed graph, this path is the same, but that is not always the case

    assert dfs_path == bfs_path

    bfs_result = breadth_first_search('B3', lambda x: x == 'A4', graph.neighbors_for_vertex)
    assert bfs_result is not None
    assert node_to_path(bfs_result) == ['B3', 'B2', 'B1', 'A4']


def test_directed_graph():
    graph = create_directed_graph()

    assert graph.vertex_count == 8
    assert graph.edge_count == 7

    assert graph.neighbors_for_vertex('B1') == ['B2', 'B4']
    assert len(graph.edges_for_vertex('B1')) == 2

    dfs_result = depth_first_search('A1', lambda x: x == 'B3', graph.neighbors_for_vertex)
    assert dfs_result is not None

    dfs_path: List[V] = node_to_path(dfs_result)

    bfs_result = breadth_first_search('A1', lambda x: x == 'B3', graph.neighbors_for_vertex)
    assert bfs_result is not None

    bfs_path: List[V] = node_to_path(bfs_result)

    # For this particular directed graph, this path is the same, but that is not always the case

    assert dfs_path == bfs_path

    bfs_result = breadth_first_search('B1', lambda x: x == 'A4', graph.neighbors_for_vertex)
    assert bfs_result is None
