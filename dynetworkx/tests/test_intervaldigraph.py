import dynetworkx as dnx
import networkx as nx


def test_intervaldigraph_init():
    G = dnx.IntervalDiGraph()
    assert G.graph == {}
    assert G._node == {}
    assert G._pred == {}
    assert G._succ == {}
    assert G.name == ''


def test_intervaldigraph_add_edge():
    G = dnx.IntervalDiGraph()
    G.add_edge(1, 2, 3, 4)
    G.add_edge(1, 3, 4, 5, weight=7, capacity=15, length=342.7)

    assert list(G.edges(data=True)) == [((1, 2, 3, 4), {}), ((1, 3, 4, 5), {'capacity': 15, 'length': 342.7, 'weight': 7})]


def test_intervaldigraph_has_edge():
    G = dnx.IntervalDiGraph()
    G.add_edges_from([(1, 2, 10, 11), (2, 4, 11, 12)])
    assert G.has_edge(1, 2)

    assert G.has_edge(1, 2, begin=2) == True
    assert G.has_edge(2, 1, begin=2) == False
    assert G.has_edge(2, 4, begin=12) == False


def test_intervaldigraph_edges_default():
    G = dnx.IntervalDiGraph()
    G.add_edge(3, 4, 5, 6)

    assert list(G.edges()) == [(3, 4, 5, 6)]


def test_intervaldigraph_edges_zero():
    G = dnx.IntervalDiGraph()
    G.add_edge(0, 4, 5, 6)
    G.add_edge(3, 4, 5, 6)

    assert list(G.edges(u=0)) == [(0, 4, 5, 6)]


def test_intervaldigraph_edges_slice():
    G = dnx.IntervalDiGraph()
    G.add_edges_from([(1, 2, 10, 11), (2, 4, 11, 12), (6, 4, 19, 20), (2, 4, 15, 16)])

    assert list(G.edges(begin=10)) == [(1, 2, 10, 11), (2, 4, 11, 12), (2, 4, 15, 16), (6, 4, 19, 20)]
    assert list(G.edges(end=11)) == [(1, 2, 10, 11)]
    assert list(G.edges(begin=11, end=15)) == [(2, 4, 11, 12)]
    assert list(G.edges(u=2)) == [(2, 4, 11, 12), (2, 4, 15, 16)]
    assert list(G.edges(v=2)) == [(1, 2, 10, 11)]
    assert list(G.edges(u=2, begin=11)) == [(2, 4, 11, 12), (2, 4, 15, 16)]
    assert list(G.edges(u=2, v=4, end=12)) == [(2, 4, 11, 12)]
    assert list(G.edges(u=1, v=2)) == [(1, 2, 10, 11)]


def test_intervaldigraph_edges_data():
    G = dnx.IntervalDiGraph()
    G.add_edge(1, 3, 4, 5, weight=8, height=18)
    G.add_edge(1, 2, 10, 11, weight=10)
    G.add_edge(2, 6, 10, 11)

    assert list(G.edges(data="weight")) == [((1, 3, 4, 5), 8), ((1, 2, 10, 11), 10), ((2, 6, 10, 11), None)]
    assert list(G.edges(data="weight", default=5)) == [((1, 3, 4, 5), 8), ((1, 2, 10, 11), 10), ((2, 6, 10, 11), 5)]
    assert list(G.edges(data=True)) == [((1, 3, 4, 5), {'height': 18, 'weight': 8}), ((1, 2, 10, 11), {'weight': 10}), ((2, 6, 10, 11), {})]
    assert list(G.edges(u=1, begin=2, end=9, data="weight")) == [((1, 3, 4, 5), 8)]


def test_intervaldigraph_remove_edge_default():
    G = dnx.IntervalDiGraph()
    G.add_edges_from([(1, 2, 10, 11), (2, 4, 11, 12), (6, 4, 9, 10), (1, 2, 15, 16)])

    assert G.has_edge(1, 2)
    G.remove_edge(1, 2)
    assert G.has_edge(1, 2) == False


def test_intervaldigraph_remove_edge_slice():
    G = dnx.IntervalDiGraph()
    G.add_edges_from([(1, 2, 10, 11), (2, 4, 11, 12), (6, 4, 9, 10), (1, 2, 15, 16)])

    assert G.has_edge(1, 2, begin=2, end=11)
    G.remove_edge(1, 2, begin=2, end=11)
    assert G.has_edge(1, 2, begin=2, end=11) == False
    assert G.has_edge(1, 2)


def test_intervaldigraph_degree():
    G = dnx.IntervalDiGraph()
    G.add_edge(1, 2, 3, 5)
    G.add_edge(2, 3, 8, 11)
    assert G.degree(2) == 2
    assert G.degree(2, 2) == 2
    assert G.degree(2, end=8) == 1
    assert G.degree() == 4 / 3
    assert G.degree(2, delta=True) == [(3, 1), (5, 0), (8, 1)]


def test_intervaldigraph_in_degree():
    G = dnx.IntervalDiGraph()
    G.add_edge(1, 2, 3, 5)
    G.add_edge(2, 3, 8, 11)
    assert G.in_degree(2) == 1
    assert G.in_degree(2, 2) == 1
    assert G.in_degree(2, end=8) == 1
    assert G.in_degree() == 2 / 3
    assert G.in_degree(2, delta=True) == [(3, 1), (5, 0)]


def test_intervaldigraph_out_degree():
    G = dnx.IntervalDiGraph()
    G.add_edge(1, 2, 3, 5)
    G.add_edge(2, 3, 8, 11)
    assert G.out_degree(2) == 1
    assert G.out_degree(2, 2) == 1
    assert G.out_degree(2, end=8) == 0
    assert G.out_degree() == 2 / 3
    assert G.out_degree(2, delta=True) == [(8, 1)]
