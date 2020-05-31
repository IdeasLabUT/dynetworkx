from intervaltree import Interval

import dynetworkx as dnx
import networkx as nx


def test_diimpulsegraph_init_default():
    G = dnx.DiImpulseGraph()
    assert G.graph == {}
    assert G._node == {}
    assert G._pred == {}
    assert G._succ == {}
    assert G.name == ''
    assert G.edgeid == 0


def test_diimpulsegraph_add_edge():
    G = dnx.DiImpulseGraph()
    G.add_edge(1, 2, 3)
    G.add_edge(1, 3, 4, weight=7, capacity=15, length=342.7)

    assert list(G.edges(data=True)) == [((1, 2, 3), {}),
                                        ((1, 3, 4), {'capacity': 15, 'length': 342.7, 'weight': 7})]


def test_diimpulsegraph_add_edges_from():
    G = dnx.DiImpulseGraph()
    G.add_edges_from([(1, 2, 10), (2, 4, 11)])
    G.add_edges_from([(3, 4, 19), (1, 4, 3)], label='WN2898')

    assert list(G.edges(data=True)) == [((1, 4, 3), {'label': 'WN2898'}),
                                        ((1, 2, 10), {}),
                                        ((2, 4, 11), {}),
                                        ((3, 4, 19), {'label': 'WN2898'})]


def test_diimpulsegraph_has_edge():
    G = dnx.DiImpulseGraph()
    G.add_edges_from([(1, 2, 10), (2, 4, 11)])
    assert G.has_edge(1, 2)

    assert G.has_edge(1, 2, begin=2) == True
    assert G.has_edge(2, 1, begin=2) == False
    assert G.has_edge(2, 4, begin=12) == False


def test_diimpulsegraph_edges_default():
    G = dnx.DiImpulseGraph()
    G.add_edge(3, 4, 5)

    assert list(G.edges()) == [(3, 4, 5)]


def test_diimpulsegraph_edges_slice():
    G = dnx.DiImpulseGraph()
    G.add_edges_from([(1, 2, 10), (2, 4, 11), (6, 4, 19), (2, 4, 15)])

    assert list(G.edges(begin=10)) == [(1, 2, 10), (2, 4, 11), (2, 4, 15), (6, 4, 19)]
    assert list(G.edges(end=11)) == [(1, 2, 10), (2, 4, 11)]
    assert list(G.edges(begin=11, end=15)) == [(2, 4, 11), (2, 4, 15)]
    assert list(G.edges(u=2)) == [(2, 4, 11), (2, 4, 15)]
    assert list(G.edges(v=2)) == [(1, 2, 10)]
    assert list(G.edges(u=2, begin=11)) == [(2, 4, 11), (2, 4, 15)]
    assert list(G.edges(u=2, v=4, end=11)) == [(2, 4, 11)]
    assert list(G.edges(u=1, v=2)) == [(1, 2, 10)]


def test_diimpulsegraph_edges_data():
    G = dnx.DiImpulseGraph()
    G.add_edge(1, 3, 4, weight=8, height=18)
    G.add_edge(1, 2, 10, weight=10)
    G.add_edge(2, 6, 10)

    assert list(G.edges(data="weight")) == [((1, 3, 4), 8), ((1, 2, 10), 10), ((2, 6, 10), None)]
    assert list(G.edges(data="weight", default=5)) == [((1, 3, 4), 8), ((1, 2, 10), 10), ((2, 6, 10), 5)]
    assert list(G.edges(data=True)) == [((1, 3, 4), {'weight': 8, 'height': 18}), ((1, 2, 10), {'weight': 10}),
                                        ((2, 6, 10), {})]
    assert list(G.edges(u=1, begin=2, end=9, data="weight")) == [((1, 3, 4), 8)]


def test_diimpulsegraph_remove_edge_default():
    G = dnx.DiImpulseGraph()
    G.add_edges_from([(1, 2, 10), (2, 4, 11), (6, 4, 9), (1, 2, 15)])

    assert G.has_edge(1, 2)
    G.remove_edge(1, 2)
    assert G.has_edge(1, 2) == False


def test_diimpulsegraph_remove_edge_slice():
    G = dnx.DiImpulseGraph()
    G.add_edges_from([(1, 2, 10), (2, 4, 11), (6, 4, 9), (1, 2, 15)])

    assert G.has_edge(1, 2, begin=2, end=11)
    G.remove_edge(1, 2, begin=2, end=11)
    assert G.has_edge(1, 2, begin=2, end=11) == False
    assert G.has_edge(1, 2)
