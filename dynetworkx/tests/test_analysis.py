import dynetworkx as dnx

def test_impulsegraph_degree():
    G = dnx.ImpulseGraph()
    G.add_edge(1, 2, 3)
    G.add_edge(2, 3, 8)
    assert G.degree(2) == 2
    assert G.degree(2, 2) == 2
    assert G.degree(2, end=8, inclusive=(True,False)) == 1
    assert G.degree() == 4/3
    assert G.degree(2, delta=True) == [(3, 1), (8, 1)]

def test_intervalgraph_degree():
    G = dnx.IntervalGraph()
    G.add_edge(1, 2, 3, 5)
    G.add_edge(2, 3, 8, 11)
    assert G.degree(2) == 2
    assert G.degree(2, 2) == 2
    assert G.degree(2, end=8) == 1
    assert G.degree() == 4/3
    assert G.degree(2, delta=True) == [(3, 1), (5, 0), (8, 1)]

def test_snapshotgraph_degree():
    G = dnx.SnapshotGraph()
    G.add_snapshot([(1, 2), (1, 3)])
    G.add_snapshot([(1, 4), (1, 3)])
    assert list(G.degree([1])[0]) == [(1, 2), (4, 1), (3, 1)]
    assert [list(G.degree(nbunch=[1, 2])[0]), list(G.degree(nbunch=[1, 2])[1])] == [[(1, 2), (2, 1)], [(1, 2)]]