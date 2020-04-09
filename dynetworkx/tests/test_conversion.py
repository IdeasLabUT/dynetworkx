import dynetworkx as dnx
import networkx as nx

def test_impulsegraph_from_networkx_graph_default():
    desired = dnx.ImpulseGraph()
    desired.add_edge(1,2,10,weight=1.5)
    desired.add_edge(2,3,11)


    graph = nx.Graph()
    graph.add_edge(1, 2, timestamp=10, weight=1.5)
    graph.add_edge(2, 3, timestamp=11)

    actual = dnx.ImpulseGraph.from_networkx_graph(graph)

    assert actual.edges(data=True) == desired.edges(data=True)

def test_impulsegraph_from_networkx_graph_timestamp():
    desired = dnx.ImpulseGraph()
    desired.add_edge(1,2,10,weight=1.5)
    desired.add_edge(2,3,11)


    graph = nx.Graph()
    graph.add_edge(1, 2, custom=10, weight=1.5)
    graph.add_edge(2, 3, custom=11)

    actual = dnx.ImpulseGraph.from_networkx_graph(graph,timestamp="custom")

    assert actual.edges(data=True) == desired.edges(data=True)

def test_impulsegraph_to_snapshots_default():
    G = dnx.ImpulseGraph()
    G.add_edges_from([(1, 2, 10), (2, 4, 11), (6, 4, 19), (2, 4, 15)])
    S = G.to_snapshots(2)

    n1 = nx.Graph()
    n1.add_edge(1,2,timestamp=10)
    n1.add_edge(2,4,timestamp=11)

    n2 = nx.Graph()
    n2.add_edge(2,4,timestamp=15)
    n2.add_edge(4,6,timestamp=19)

    nl = [n1,n2]

    for i in range(len(S)):
        assert list(S[i].edges()) == list(nl[i].edges())

def test_impulsegraph_to_snapshots_multigraph():
    G = dnx.ImpulseGraph()
    G.add_edges_from([(1, 2, 10), (1, 2, 11), (6, 4, 19), (2, 4, 15)])
    S = G.to_snapshots(2, edge_timestamp_data=True, multigraph=True)

    n1 = nx.MultiGraph()
    n1.add_edge(1,2,timestamp=10)
    n1.add_edge(1,2,timestamp=11)

    n2 = nx.MultiGraph()
    n2.add_edge(2,4,timestamp=15)
    n2.add_edge(4,6,timestamp=19)

    nl = [n1,n2]

    for i in range(len(S)):
        assert list(S[i].edges(data=True)) == list(nl[i].edges(data=True))
        assert type(S[i]) == type(nl[i])

def test_impulsegraph_to_snapshots_edge_data():
    G = dnx.ImpulseGraph()
    G.add_edge(1, 2, 10, weight=1.9)
    G.add_edge(2, 4, 11, weight=1.4)
    G.add_edge(2, 4, 15, weight=1.3)
    G.add_edge(4, 6, 19, weight=1)
    S = G.to_snapshots(2, edge_data=True)

    n1 = nx.Graph()
    n1.add_edge(1, 2, weight=1.9)
    n1.add_edge(2, 4, weight=1.4)

    n2 = nx.Graph()
    n2.add_edge(2, 4, weight=1.3)
    n2.add_edge(4, 6, weight=1)

    nl = [n1,n2]

    for i in range(len(S)):
        assert list(S[i].edges(data=True)) == list(nl[i].edges(data=True))

def test_impulsegraph_to_snapshots_edge_timestamp_data():
    G = dnx.ImpulseGraph()
    G.add_edge(1, 2, 10)
    G.add_edge(2, 4, 11)
    G.add_edge(2, 4, 15)
    G.add_edge(4, 6, 19)
    S = G.to_snapshots(2, edge_timestamp_data=True)

    n1 = nx.Graph()
    n1.add_edge(1, 2, timestamp=10)
    n1.add_edge(2, 4, timestamp=11)

    n2 = nx.Graph()
    n2.add_edge(2, 4, timestamp=15)
    n2.add_edge(4, 6, timestamp=19)

    nl = [n1,n2]

    for i in range(len(S)):
        assert list(S[i].edges(data=True)) == list(nl[i].edges(data=True))

def test_impulsegraph_to_snapshots_node_data():
    G = dnx.ImpulseGraph()
    G.add_node(1, size=1.5)
    G.add_node(2, size=0)
    G.add_edge(1, 2, 10)
    G.add_edge(2, 4, 11)
    G.add_edge(2, 4, 15)
    G.add_edge(4, 6, 19)
    S = G.to_snapshots(2, node_data=True)

    n1 = nx.Graph()
    n1.add_node(1, size=1.5)
    n1.add_node(2, size=0)
    n1.add_edge(1, 2)
    n1.add_edge(2, 4)

    n2 = nx.Graph()
    n2.add_node(2, size=0)
    n2.add_edge(2, 4)
    n2.add_edge(4, 6)

    nl = [n1,n2]

    for i in range(len(S)):
        assert list(S[i].edges(data=True)) == list(nl[i].edges(data=True))
        assert list(S[i].nodes(data=True)) == list(nl[i].nodes(data=True))

def test_impulsegraph_to_subgraph_default():
    G = dnx.ImpulseGraph()
    G.add_edges_from([(1, 2, 10), (2, 4, 11), (6, 4, 19), (2, 4, 15)])
    H = G.to_subgraph(4, 12)

    assert list(H.edges(data=True)) == [(1, 2, {}), (2, 4, {})]
    assert isinstance(H,nx.classes.graph.Graph)

def test_impulsegraph_to_subgraph_edge_data():
    G = dnx.ImpulseGraph()
    G.add_edges_from([(1, 2, 10), (2, 4, 11), (6, 4, 19), (2, 4, 15)],weight=1.5)
    H = G.to_subgraph(4, 12, edge_data=True)

    assert list(H.edges(data=True)) == [(1, 2, {'weight': 1.5}), (2, 4, {'weight': 1.5})]
    assert isinstance(H,nx.classes.graph.Graph)

def test_impulsegraph_to_subgraph_node_data():
    G = dnx.ImpulseGraph()
    G.add_node(1, size=1.2)
    G.add_edges_from([(1, 2, 10), (2, 4, 11), (6, 4, 19), (2, 4, 15)])
    H = G.to_subgraph(4, 12,node_data=True)

    assert list(H.edges(data=True)) == [(1, 2, {}), (2, 4, {})]
    assert list(H.nodes(data=True)) == [(1, {'size': 1.2}), (2, {}), (4, {})]
    assert isinstance(H,nx.classes.graph.Graph)

def test_impulsegraph_to_subgraph_edge_timestamp_data():
    G = dnx.ImpulseGraph()
    G.add_edges_from([(1, 2, 10), (2, 4, 11), (6, 4, 19), (2, 4, 15)])
    H = G.to_subgraph(4, 12, edge_timestamp_data=True)

    assert list(H.edges(data=True)) == [(1, 2, {'timestamp': 10}), (2, 4, {'timestamp': 11})]
    assert isinstance(H, nx.classes.graph.Graph)

def test_impulsegraph_to_subgraph_multigraph():
    G = dnx.ImpulseGraph()
    G.add_edges_from([(1, 2, 10), (2, 4, 11), (6, 4, 19), (2, 4, 15)])
    M = G.to_subgraph(4, 12, multigraph=True)

    assert list(M.edges()) == [(1, 2), (2, 4)]
    assert isinstance(M, nx.classes.graph.Graph)

def test_intervalgraph_from_networkx_graph_default():
    desired = dnx.IntervalGraph()
    desired.add_edge(1,2,10,11,weight=1.5)
    desired.add_edge(2,3,11,12)


    graph = nx.Graph()
    graph.add_edge(1, 2, begin=10, end=11, weight=1.5)
    graph.add_edge(2, 3, begin=11, end=12)

    actual = dnx.IntervalGraph.from_networkx_graph(graph)

    assert actual.edges(data=True) == desired.edges(data=True)

def test_intervalgraph_from_networkx_graph_timestamp():
    desired = dnx.IntervalGraph()
    desired.add_edge(1,2,10,11,weight=1.5)
    desired.add_edge(2,3,11,12)


    graph = nx.Graph()
    graph.add_edge(1, 2, custom_begin=10, custom_end=11, weight=1.5)
    graph.add_edge(2, 3, custom_begin=11, custom_end=12)

    actual = dnx.IntervalGraph.from_networkx_graph(graph,begin="custom_begin",end="custom_end")

    assert actual.edges(data=True) == desired.edges(data=True)

def test_intervalgraph_from_snapshots_default():
    desired = dnx.IntervalGraph()
    desired.add_edge(1,2,0,1)
    desired.add_edge(6,7,0,1)
    desired.add_edge(5,6,0,1)
    desired.add_edge(1,4,1,2)
    desired.add_edge(1,3,0,2)
    desired.add_edge(10,11,0,2)
    desired.add_edge(8,9,0,2,weight=1)

    sg = dnx.SnapshotGraph()
    sg.add_snapshot([(1, 2), (1, 3)])
    sg.add_snapshot([(1, 4), (1, 3)])
    sg.add_edges_from([(5, 6), (7, 6)], [0])
    sg.add_edges_from([(8, 9), (10, 11)], [0, 1])
    sg.add_edges_from([(8, 9)], weight=1)

    actual = dnx.IntervalGraph.from_snapshots(sg)

    assert sorted(actual.edges(data=True)) == sorted(desired.edges(data=True))

def test_intervalgraph_from_snapshots_begin():
    desired = dnx.IntervalGraph()
    desired.add_edge(1,2,10,11)
    desired.add_edge(6,7,10,11)
    desired.add_edge(5,6,10,11)
    desired.add_edge(1,4,11,12)
    desired.add_edge(1,3,10,12)
    desired.add_edge(10,11,10,12)
    desired.add_edge(8,9,10,12,weight=1)

    sg = dnx.SnapshotGraph()
    sg.add_snapshot([(1, 2), (1, 3)])
    sg.add_snapshot([(1, 4), (1, 3)])
    sg.add_edges_from([(5, 6), (7, 6)], [0])
    sg.add_edges_from([(8, 9), (10, 11)], [0, 1])
    sg.add_edges_from([(8, 9)], weight=1)

    actual = dnx.IntervalGraph.from_snapshots(sg, begin=10)

    assert sorted(actual.edges(data=True)) == sorted(desired.edges(data=True))

def test_intervalgraph_from_snapshots_period():
    desired = dnx.IntervalGraph()
    desired.add_edge(1,2,0,2)
    desired.add_edge(6,7,0,2)
    desired.add_edge(5,6,0,2)
    desired.add_edge(1,4,2,4)
    desired.add_edge(1,3,0,4)
    desired.add_edge(10,11,0,4)
    desired.add_edge(8,9,0,4,weight=1)

    sg = dnx.SnapshotGraph()
    sg.add_snapshot([(1, 2), (1, 3)])
    sg.add_snapshot([(1, 4), (1, 3)])
    sg.add_edges_from([(5, 6), (7, 6)], [0])
    sg.add_edges_from([(8, 9), (10, 11)], [0, 1])
    sg.add_edges_from([(8, 9)], weight=1)

    actual = dnx.IntervalGraph.from_snapshots(sg, period=2)

    assert sorted(actual.edges(data=True)) == sorted(desired.edges(data=True))

def test_intervalgraph_to_snapshots_default():
    G = dnx.IntervalGraph()
    G.add_edges_from([(1, 2, 3, 6), (2, 4, 5, 11), (6, 4, 19, 20), (2, 4, 15, 16)])
    S = G.to_snapshots(2)

    assert sorted(list(S[0].edges())) == [(1, 2), (2, 4)]
    assert sorted(list(S[1].edges())) == [(4, 2), (6, 4)]

def test_intervalgraph_to_subgraph_default():
    G = dnx.IntervalGraph()
    G.add_edges_from([(1, 2, 3, 6), (2, 4, 5, 11), (6, 4, 19, 20), (2, 4, 15, 16)])
    H = G.to_subgraph(4, 12)

    assert sorted(list(H.edges())) == [(1, 2), (2, 4)]
    assert isinstance(H, nx.classes.graph.Graph)

def test_intervalgraph_to_subgraph_edge_data():
    G = dnx.IntervalGraph()
    G.add_edges_from([(1, 2, 3, 6), (2, 4, 5, 11), (6, 4, 19, 20), (2, 4, 15, 16)], weight=1.5)
    H = G.to_subgraph(4, 12, edge_data=True)

    assert list(H.edges(data=True)) == [(1, 2, {'weight': 1.5}), (2, 4, {'weight': 1.5})]
    assert isinstance(H,nx.classes.graph.Graph)

def test_intervalgraph_to_subgraph_node_data():
    G = dnx.IntervalGraph()
    G.add_node(1, size=1.2)
    G.add_edges_from([(1, 2, 3, 6), (2, 4, 5, 11), (6, 4, 19, 20), (2, 4, 15, 16)])
    H = G.to_subgraph(4, 12,node_data=True)

    assert list(H.edges()) == [(1, 2), (2, 4)]
    assert list(H.nodes(data=True)) == [(1, {'size': 1.2}), (2, {}), (4, {})]
    assert isinstance(H,nx.classes.graph.Graph)

def test_intervalgraph_to_subgraph_edge_interval_data():
    G = dnx.IntervalGraph()
    G.add_edges_from([(1, 2, 3, 6), (2, 4, 5, 11), (6, 4, 19, 20), (2, 4, 15, 16)])
    H = G.to_subgraph(4, 12, edge_interval_data=True)

    assert list(H.edges(data=True)) == [(1, 2, {'begin': 3, 'end': 6}), (2, 4, {'begin': 5, 'end': 11})]
    assert isinstance(H, nx.classes.graph.Graph)

def test_intervalgraph_to_subgraph_multigraph():
    G = dnx.IntervalGraph()
    G.add_edges_from([(1, 2, 3, 6), (2, 4, 5, 11), (6, 4, 19, 20), (2, 4, 15, 16)])
    M = G.to_subgraph(4, 12, multigraph=True)

    assert list(M.edges()) == [(1, 2), (2, 4)]
    assert isinstance(M, nx.classes.graph.Graph)