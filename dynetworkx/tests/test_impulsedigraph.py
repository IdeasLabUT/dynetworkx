import dynetworkx as dnx
import networkx as nx


def test_impulsedigraph_init_default():
    G = dnx.ImpulseDiGraph()
    assert G.graph == {}
    assert G._node == {}
    assert G._pred == {}
    assert G._succ == {}
    assert G.name == ''
    assert G.edgeid == 0


def test_impulsedigraph_add_edge():
    G = dnx.ImpulseDiGraph()
    G.add_edge(1, 2, 3)
    G.add_edge(1, 3, 4, weight=7, capacity=15, length=342.7)

    assert list(G.edges(data=True)) == [((1, 2, 3), {}),
                                        ((1, 3, 4), {'capacity': 15, 'length': 342.7, 'weight': 7})]


def test_impulsedigraph_add_edges_from():
    G = dnx.ImpulseDiGraph()
    G.add_edges_from([(1, 2, 10), (2, 4, 11)])
    G.add_edges_from([(3, 4, 19), (1, 4, 3)], label='WN2898')

    assert list(G.edges(data=True)) == [((1, 4, 3), {'label': 'WN2898'}),
                                        ((1, 2, 10), {}),
                                        ((2, 4, 11), {}),
                                        ((3, 4, 19), {'label': 'WN2898'})]


def test_impulsedigraph_has_edge():
    G = dnx.ImpulseDiGraph()
    G.add_edges_from([(1, 2, 10), (2, 4, 11)])
    assert G.has_edge(1, 2)

    assert G.has_edge(1, 2, begin=2) == True
    assert G.has_edge(2, 1, begin=2) == False
    assert G.has_edge(2, 4, begin=12) == False


def test_impulsedigraph_edges_default():
    G = dnx.ImpulseDiGraph()
    G.add_edge(3, 4, 5)

    assert list(G.edges()) == [(3, 4, 5)]


def test_impulsedigraph_edges_zero():
    G = dnx.ImpulseDiGraph()
    G.add_edge(0, 4, 5)
    G.add_edge(3, 4, 5)

    assert list(G.edges(u=0)) == [(0, 4, 5)]


def test_impulsedigraph_edges_slice():
    G = dnx.ImpulseDiGraph()
    G.add_edges_from([(1, 2, 10), (2, 4, 11), (6, 4, 19), (2, 4, 15)])

    assert list(G.edges(begin=10)) == [(1, 2, 10), (2, 4, 11), (2, 4, 15), (6, 4, 19)]
    assert list(G.edges(end=11)) == [(1, 2, 10), (2, 4, 11)]
    assert list(G.edges(begin=11, end=15)) == [(2, 4, 11), (2, 4, 15)]
    assert list(G.edges(u=2)) == [(2, 4, 11), (2, 4, 15)]
    assert list(G.edges(v=2)) == [(1, 2, 10)]
    assert list(G.edges(u=2, begin=11)) == [(2, 4, 11), (2, 4, 15)]
    assert list(G.edges(u=2, v=4, end=11)) == [(2, 4, 11)]
    assert list(G.edges(u=1, v=2)) == [(1, 2, 10)]


def test_impulsedigraph_edges_data():
    G = dnx.ImpulseDiGraph()
    G.add_edge(1, 3, 4, weight=8, height=18)
    G.add_edge(1, 2, 10, weight=10)
    G.add_edge(2, 6, 10)

    assert list(G.edges(data="weight")) == [((1, 3, 4), 8), ((1, 2, 10), 10), ((2, 6, 10), None)]
    assert list(G.edges(data="weight", default=5)) == [((1, 3, 4), 8), ((1, 2, 10), 10), ((2, 6, 10), 5)]
    assert list(G.edges(data=True)) == [((1, 3, 4), {'weight': 8, 'height': 18}), ((1, 2, 10), {'weight': 10}),
                                        ((2, 6, 10), {})]
    assert list(G.edges(u=1, begin=2, end=9, data="weight")) == [((1, 3, 4), 8)]


def test_impulsedigraph_remove_edge_default():
    G = dnx.ImpulseDiGraph()
    G.add_edges_from([(1, 2, 10), (2, 4, 11), (6, 4, 9), (1, 2, 15)])

    assert G.has_edge(1, 2)
    G.remove_edge(1, 2)
    assert G.has_edge(1, 2) == False


def test_impulsedigraph_remove_edge_slice():
    G = dnx.ImpulseDiGraph()
    G.add_edges_from([(1, 2, 10), (2, 4, 11), (6, 4, 9), (1, 2, 15)])

    assert G.has_edge(1, 2, begin=2, end=11)
    G.remove_edge(1, 2, begin=2, end=11)
    assert G.has_edge(1, 2, begin=2, end=11) == False
    assert G.has_edge(1, 2)


def test_impulsedigraph_degree():
    G = dnx.ImpulseDiGraph()
    G.add_edge(1, 2, 3)
    G.add_edge(2, 3, 8)
    assert G.degree(2) == 2
    assert G.degree(2, 4) == 1
    assert G.degree(2, end=8) == 2
    assert G.degree() == 4/3
    assert G.degree(2, delta=True) == [(3, 1), (8, 1)]


def test_impulsedigraph_in_degree():
    G = dnx.ImpulseDiGraph()
    G.add_edge(1, 2, 3)
    G.add_edge(2, 3, 8)
    assert G.in_degree(2) == 1
    assert G.in_degree(2, 4) == 0
    assert G.in_degree(2, end=8) == 1
    assert G.in_degree() == 2/3
    assert G.in_degree(2, delta=True) == [(3, 1)]


def test_impulsedigraph_out_degree():
    G = dnx.ImpulseDiGraph()
    G.add_edge(1, 2, 3)
    G.add_edge(2, 3, 8)
    assert G.out_degree(2) == 1
    assert G.out_degree(2, 4) == 1
    assert G.out_degree(2, end=8) == 1
    assert G.out_degree() == 2/3
    assert G.out_degree(2, delta=True) == [(8, 1)]
