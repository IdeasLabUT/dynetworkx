import dynetworkx as dnx
import networkx as nx
from intervaltree import Interval

def test_impulsegraph_init_default():
    G = dnx.ImpulseGraph()
    assert G.graph == {}
    assert G._node == {}
    assert G._adj == {}
    assert G.name == ''
    assert G.edgeid == 0

def test_impulsegraph_init_default():
    G = dnx.ImpulseGraph()
    assert G.graph == {}
    assert G._node == {}
    assert G._adj == {}
    assert G.name == ''
    assert G.edgeid == 0

def test_impulsegraph_init_name():
    G = dnx.ImpulseGraph(name='test_name')
    assert G.graph['name'] == 'test_name'
    assert G.name == 'test_name'

def test_impulsegraph_init_attr():
    G = dnx.ImpulseGraph(unique_test=123)
    assert G.graph['unique_test'] == 123

def test_impulsegraph_str():
    G = dnx.ImpulseGraph(name='test_name')
    assert str(G) == 'test_name'

def test_impulsegraph_len():
    G = dnx.ImpulseGraph()
    G.add_nodes_from([0,1,2])
    assert len(G) == 3

def test_impulsegraph_contains():
    G = dnx.ImpulseGraph()
    G.add_node(2)
    assert 2 in G

def test_impulsegraph_interval():
    G = dnx.ImpulseGraph()
    G.add_edges_from([(1, 2, 10), (3, 7, 16)])
    assert G.interval() == (10,16)

def test_impulsegraph_add_node():
    G = dnx.ImpulseGraph()
    G.add_node(1)
    G.add_node('Hello')
    G.add_node(3, weight=0.1)

    assert G.number_of_nodes() == 3
    assert G._node[3]['weight'] == 0.1

def test_impulsegraph_add_nodes_from():
    G = dnx.ImpulseGraph()
    G.add_nodes_from('Hello')
    G.add_nodes_from([1, 2], size=10)

    assert 'e' in G._node
    assert G._node[1]['size'] == 10

def test_impulsegraph_number_of_nodes():
    G = dnx.ImpulseGraph()
    G.add_edges_from([(1, 2, 5), (3, 4, 11)])

    assert G.number_of_nodes() == 4
    assert G.number_of_nodes(begin=6) == 2
    assert G.number_of_nodes(begin=5, end=8) == 2
    assert G.number_of_nodes(end=11) == 4

def test_impulsegraph_has_node():
    G = dnx.ImpulseGraph()
    G.add_node(1)
    G.add_edge(3,4,5)

    assert G.has_node(1)
    assert G.has_node(3, begin=2)
    assert G.has_node(3, end=2) == False

def test_impulsegraph_nodes_default():
    G = dnx.ImpulseGraph()
    G.add_node(1)
    G.add_edge(3,4,5)

    assert list(G.nodes()) == [1,3,4]

def test_impulsegraph_nodes_slice():
    G = dnx.ImpulseGraph()
    G.add_edge(1,2,3)
    G.add_edge(4,5,6)
    G.add_edge(7,8,9)

    assert sorted(list(G.nodes(begin=4))) == [4,5,7,8]
    assert sorted(list(G.nodes(end=7))) == [1,2,4,5]
    assert sorted(list(G.nodes(4,7))) == [4,5]

def test_impulsegraph_nodes_data():
    G = dnx.ImpulseGraph()
    G.add_node(1,size=1.2)
    G.add_node(2)

    assert list(G.nodes(data=True)) == [(1,{'size':1.2}),(2,{})]

def test_impulsegraph_remove_node_default():
    G = dnx.ImpulseGraph()
    G.add_edges_from([(1, 2, 10), (2, 4, 11), (6, 4, 19), (2, 4, 15)])
    G.remove_node(6)
    assert list(G.nodes()) == [1,2,4]

def test_impulsegraph_remove_node_slice():
    G = dnx.ImpulseGraph()
    G.add_edges_from([(1, 2, 10), (2, 4, 11), (6, 4, 19), (2, 4, 15)])
    assert G.has_node(2,begin=11) == True
    assert G.has_node(4, end=13) == True

    G.remove_node(2,begin=11)
    G.remove_node(4,end=13)

    assert list(G.nodes()) == [1,2,4,6]
    assert G.has_node(2,begin=11) == False
    assert G.has_node(4,end=13) == False

def test_impulsegraph_add_edge():
    G = dnx.ImpulseGraph()
    G.add_edge(1, 2, 3)
    G.add_edge(1, 3, 4, weight=7, capacity=15, length=342.7)

    assert list(G.edges(data=True)) == [((1, 2, 3), {}),
                                        ((1, 3, 4), {'capacity': 15, 'length': 342.7, 'weight': 7})]

def test_impulsegraph_add_edges_from():
    G = dnx.ImpulseGraph()
    G.add_edges_from([(1, 2, 10), (2, 4, 11)])
    G.add_edges_from([(3, 4, 19), (1, 4, 3)], label='WN2898')

    assert list(G.edges(data=True)) == [((1, 4, 3), {'label': 'WN2898'}),
                                        ((1, 2, 10), {}),
                                        ((2, 4, 11), {}),
                                        ((3, 4, 19), {'label': 'WN2898'})]

def test_impulsegraph_has_edge():
    G = dnx.ImpulseGraph()
    G.add_edges_from([(1, 2, 10), (2, 4, 11)])
    assert G.has_edge(1, 2)

    assert G.has_edge(1, 2, begin=2) == True
    assert G.has_edge(2, 4, begin=12) == False

def test_impulsegraph_edges_default():
    G = dnx.ImpulseGraph()
    G.add_edge(3,4,5)

    assert list(G.edges()) == [(3,4,5)]

def test_impulsegraph_edges_slice():
    G = dnx.ImpulseGraph()
    G.add_edges_from([(1, 2, 10), (2, 4, 11), (6, 4, 19), (2, 4, 15)])

    assert list(G.edges(begin=10)) == [(1, 2, 10), (2, 4, 11), (2, 4, 15), (6, 4, 19)]
    assert list(G.edges(end=11)) == [(1, 2, 10), (2, 4, 11)]
    assert list(G.edges(begin=11, end=15)) == [(2, 4, 11), (2, 4, 15)]
    assert list(G.edges(u=2)) == [(1, 2, 10), (2, 4, 11), (2, 4, 15)]
    assert list(G.edges(v=2)) == [(1, 2, 10), (2, 4, 11), (2, 4, 15)]
    assert list(G.edges(u=2, begin=11)) == [(2, 4, 11), (2, 4, 15)]
    assert list(G.edges(u=2, v=4, end=11)) == [(2, 4, 11)]
    assert list(G.edges(u=1, v=2)) == [(1, 2, 10)]

def test_impulsegraph_edges_data():
    G = dnx.ImpulseGraph()
    G.add_edge(1, 3, 4, weight=8, height=18)
    G.add_edge(1, 2, 10, weight=10)
    G.add_edge(2, 6, 10)

    assert list(G.edges(data="weight")) == [((1, 3, 4), 8), ((1, 2, 10), 10), ((2, 6, 10), None)]
    assert list(G.edges(data="weight", default=5)) == [((1, 3, 4), 8), ((1, 2, 10), 10), ((2, 6, 10), 5)]
    assert list(G.edges(data=True)) == [((1, 3, 4), {'weight': 8, 'height': 18}), ((1, 2, 10), {'weight': 10}), ((2, 6, 10), {})]
    assert list(G.edges(u=1, begin=2, end=9, data="weight")) == [((1, 3, 4), 8)]

def test_impulsegraph_remove_edge_default():
    G = dnx.ImpulseGraph()
    G.add_edges_from([(1, 2, 10), (2, 4, 11), (6, 4, 9), (1, 2, 15)])

    assert G.has_edge(1, 2)
    G.remove_edge(1, 2)
    assert G.has_edge(1, 2) == False

def test_impulsegraph_remove_edge_slice():
    G = dnx.ImpulseGraph()
    G.add_edges_from([(1, 2, 10), (2, 4, 11), (6, 4, 9), (1, 2, 15)])

    assert G.has_edge(1, 2, begin=2, end=11)
    G.remove_edge(1, 2, begin=2, end=11)
    assert G.has_edge(1, 2, begin=2, end=11) == False
    assert G.has_edge(1, 2)

def test_intervalgraph_init_default():
    G = dnx.IntervalGraph()
    assert G.graph == {}
    assert G._node == {}
    assert G._adj == {}
    assert G.name == ''

def test_intervalgraph_init_default():
    G = dnx.IntervalGraph()
    assert G.graph == {}
    assert G._node == {}
    assert G._adj == {}
    assert G.name == ''

def test_intervalgraph_init_name():
    G = dnx.IntervalGraph(name='test_name')
    assert G.graph['name'] == 'test_name'
    assert G.name == 'test_name'

def test_intervalgraph_init_attr():
    G = dnx.IntervalGraph(unique_test=123)
    assert G.graph['unique_test'] == 123

def test_intervalgraph_str():
    G = dnx.IntervalGraph(name='test_name')
    assert str(G) == 'test_name'

def test_intervalgraph_len():
    G = dnx.IntervalGraph()
    G.add_nodes_from([0, 1, 2])
    assert len(G) == 3

def test_intervalgraph_contains():
    G = dnx.IntervalGraph()
    G.add_node(2)
    assert 2 in G

def test_intervalgraph_interval():
    G = dnx.IntervalGraph()
    G.add_edges_from([(1, 2, 10, 11), (3, 7, 16, 17)])
    assert G.interval() == (10,17)

def test_intervalgraph_add_node():
    G = dnx.IntervalGraph()
    G.add_node(1)
    G.add_node('Hello')
    G.add_node(3, weight=0.1)

    assert G.number_of_nodes() == 3
    assert G._node[3]['weight'] == 0.1

def test_intervalgraph_add_nodes_from():
    G = dnx.IntervalGraph()
    G.add_nodes_from('Hello')
    G.add_nodes_from([1, 2], size=10)

    assert 'e' in G._node
    assert G._node[1]['size'] == 10

def test_intervalgraph_number_of_nodes():
    G = dnx.IntervalGraph()
    G.add_edges_from([(1, 2, 5, 6), (3, 4, 11, 12)])

    assert G.number_of_nodes() == 4
    assert G.number_of_nodes(begin=6) == 2
    assert G.number_of_nodes(begin=5, end=8) == 2
    assert G.number_of_nodes(end=11) == 2

def test_intervalgraph_has_node():
    G = dnx.IntervalGraph()
    G.add_node(1)
    G.add_edge(3,4,5,6)

    assert G.has_node(1)
    assert G.has_node(3, begin=2)
    assert G.has_node(3, end=2) == False

def test_intervalgraph_nodes_default():
    G = dnx.IntervalGraph()
    G.add_node(1)
    G.add_edge(3,4,5,6)

    assert list(G.nodes()) == [1,3,4]

def test_intervalgraph_nodes_slice():
    G = dnx.IntervalGraph()
    G.add_edge(1,2,3,4)
    G.add_edge(4,5,6,7)
    G.add_edge(7,8,9,10)

    assert sorted(list(G.nodes(begin=4))) == [4,5,7,8]
    assert sorted(list(G.nodes(end=7))) == [1,2,4,5]
    assert sorted(list(G.nodes(4,7))) == [4,5]

def test_intervalgraph_nodes_data():
    G = dnx.IntervalGraph()
    G.add_node(1,size=1.2)
    G.add_node(2)

    assert list(G.nodes(data=True)) == [(1,{'size':1.2}),(2,{})]

def test_intervalgraph_remove_node_default():
    G = dnx.IntervalGraph()
    G.add_edges_from([(1, 2, 10, 11), (2, 4, 11, 12), (6, 4, 19, 20), (2, 4, 15, 16)])
    G.remove_node(6)
    assert list(G.nodes()) == [1,2,4]

def test_intervalgraph_remove_node_slice():
    G = dnx.IntervalGraph()
    G.add_edges_from([(1, 2, 10, 11), (2, 4, 11, 12), (6, 4, 19, 20), (2, 4, 15, 16)])
    assert G.has_node(2,begin=11) == True
    assert G.has_node(4, end=13) == True

    G.remove_node(2,begin=11)
    G.remove_node(4,end=13)

    assert list(G.nodes()) == [1,2,4,6]
    assert G.has_node(2,begin=11) == False
    assert G.has_node(4,end=13) == False

def test_intervalgraph_add_edge():
    G = dnx.IntervalGraph()
    G.add_edge(1, 2, 3, 4)
    G.add_edge(1, 3, 4, 5, weight=7, capacity=15, length=342.7)

    assert list(G.edges(data=True)) == [(Interval(4, 5, (1, 3)), {'capacity': 15, 'length': 342.7, 'weight': 7}),
                                        (Interval(3, 4, (1, 2)), {})]

def test_intervalgraph_add_edges_from():
    G = dnx.IntervalGraph()
    G.add_edges_from([(1, 2, 10, 11), (2, 4, 11, 12)])
    G.add_edges_from([(3, 4, 19, 20), (1, 4, 3, 4)], label='WN2898')

    assert list(G.edges(data=True)) == [(Interval(19, 20, (3, 4)), {'label': 'WN2898'}),
                                        (Interval(11, 12, (2, 4)), {}),
                                        (Interval(10, 11, (1, 2)), {}),
                                        (Interval(3, 4, (1, 4)), {'label': 'WN2898'})]

def test_intervalgraph_has_edge():
    G = dnx.IntervalGraph()
    G.add_edges_from([(1, 2, 10, 11), (2, 4, 11, 12)])
    assert G.has_edge(1, 2)

    assert G.has_edge(1, 2, begin=2) == True
    assert G.has_edge(2, 4, begin=12) == False

def test_intervalgraph_edges_default():
    G = dnx.IntervalGraph()
    G.add_edge(3,4,5,6)

    assert list(G.edges()) == [Interval(5, 6, (3, 4))]

def test_intervalgraph_edges_slice():
    G = dnx.IntervalGraph()
    G.add_edges_from([(1, 2, 10, 11), (2, 4, 11, 12), (6, 4, 19, 20), (2, 4, 15, 16)])

    assert list(G.edges(begin=10)) == [Interval(10, 11, (1, 2)), Interval(19, 20, (6, 4)),
                                       Interval(11, 12, (2, 4)), Interval(15, 16, (2, 4))]
    assert list(G.edges(end=11)) == [Interval(10, 11, (1, 2))]
    assert list(G.edges(begin=11, end=15)) == [Interval(11, 12, (2, 4))]
    assert list(G.edges(u=2)) == [Interval(10, 11, (1, 2)), Interval(11, 12, (2, 4)), Interval(15, 16, (2, 4))]
    assert list(G.edges(v=2)) == [Interval(10, 11, (1, 2)), Interval(11, 12, (2, 4)), Interval(15, 16, (2, 4))]
    assert list(G.edges(u=2, begin=11)) == [Interval(11, 12, (2, 4)), Interval(15, 16, (2, 4))]
    assert list(G.edges(u=2, v=4, end=12)) == [Interval(11, 12, (2, 4))]
    assert list(G.edges(u=1, v=2)) == [Interval(10, 11, (1, 2))]

def test_intervalgraph_edges_data():
    G = dnx.IntervalGraph()
    G.add_edge(1, 3, 4, 5, weight=8, height=18)
    G.add_edge(1, 2, 10, 11, weight=10)
    G.add_edge(2, 6, 10, 11)

    assert list(G.edges(data="weight")) == [(Interval(4, 5, (1, 3)), 8),
                                            (Interval(10, 11, (2, 6)), None),
                                            (Interval(10, 11, (1, 2)), 10)]
    assert list(G.edges(data="weight", default=5)) == [(Interval(4, 5, (1, 3)), 8),
                                                       (Interval(10, 11, (2, 6)), 5),
                                                       (Interval(10, 11, (1, 2)), 10)]
    assert list(G.edges(data=True)) == [(Interval(4, 5, (1, 3)), {'weight': 8, 'height': 18}),
                                        (Interval(10, 11, (2, 6)), {}),
                                        (Interval(10, 11, (1, 2)), {'weight': 10})]
    assert list(G.edges(u=1, begin=2, end=9, data="weight")) == [(Interval(4, 5, (1, 3)), 8)]

def test_intervalgraph_remove_edge_default():
    G = dnx.IntervalGraph()
    G.add_edges_from([(1, 2, 10, 11), (2, 4, 11, 12), (6, 4, 9, 10), (1, 2, 15, 16)])

    assert G.has_edge(1, 2)
    G.remove_edge(1, 2)
    assert G.has_edge(1, 2) == False

def test_intervalgraph_remove_edge_slice():
    G = dnx.IntervalGraph()
    G.add_edges_from([(1, 2, 10, 11), (2, 4, 11, 12), (6, 4, 9, 10), (1, 2, 15, 16)])

    assert G.has_edge(1, 2, begin=2, end=11)
    G.remove_edge(1, 2, begin=2, end=11)
    assert G.has_edge(1, 2, begin=2, end=11) == False
    assert G.has_edge(1, 2)

def test_snapshotgraph_init_default():
    G = dnx.SnapshotGraph()
    assert G.graph == {}
    assert G.name == ''

def test_snapshotgraph_init_default():
    G = dnx.SnapshotGraph()
    assert G.graph == {}
    assert G.name == ''

def test_snapshotgraph_init_name():
    G = dnx.SnapshotGraph(name='test_name')
    assert G.graph['name'] == 'test_name'
    assert G.name == 'test_name'

def test_snapshotgraph_init_attr():
    G = dnx.SnapshotGraph(unique_test=123)
    assert G.graph['unique_test'] == 123

def test_snapshotgraph_str():
    G = dnx.SnapshotGraph(name='test_name')
    assert str(G) == 'test_name'

def test_snapshotgraph_len():
    nxG1 = nx.Graph()
    nxG2 = nx.Graph()
    nxG1.add_edges_from([(1, 2), (1, 3)])
    nxG2.add_edges_from([(1, 4), (1, 3)])

    G = dnx.SnapshotGraph()
    G.add_snapshot(graph=nxG1)
    G.add_snapshot(graph=nxG2)
    assert len(G) == 2

def test_snapshotgraph_contains():
    nxG1 = nx.Graph()
    nxG2 = nx.Graph()
    nxG1.add_edges_from([(1, 2), (1, 3)])
    nxG2.add_edges_from([(1, 4), (1, 3)])

    G = dnx.SnapshotGraph()
    G.add_snapshot(graph=nxG1)
    G.add_snapshot(graph=nxG2)

    assert nxG1 in G

def test_snapshotgraph_insert():
    G = dnx.SnapshotGraph()
    nxG1 = nx.Graph()
    nxG1.add_edges_from([(1, 2), (1, 3)])
    nxG2 = nx.Graph()
    nxG2.add_edges_from([(1, 2), (1, 3)])
    G.insert(nxG1, 0)

    assert G.snapshots == [nxG1]

    G.insert(nxG1, 2)

    assert G.snapshots == [nxG1, nxG1, nxG1]

    G.insert(nxG2, 3, 1)

    assert G.snapshots == [nxG1, nxG2, nxG2, nxG2, nxG1, nxG1]

def test_snapshotgraph_add_snapshot():
    G = dnx.SnapshotGraph()
    nxG1 = nx.Graph()
    nxG1.add_edges_from([(1, 2), (1, 3)])
    G.add_snapshot([(1, 2), (1, 3)])
    G.add_snapshot(graph=nxG1)
    assert list(G.snapshots[0].edges(data=True)) == list(nxG1.edges(data=True))
    assert list(G.snapshots[1].edges(data=True)) == list(nxG1.edges(data=True))

def test_snapshotgraph_snapshot():
    G = dnx.SnapshotGraph()
    G.add_snapshot([(1, 2), (2, 3), (4, 6), (2, 4)])
    G.add_snapshot([(1, 2), (2, 3), (4, 6), (2, 4)])
    H = G.subgraph([4, 6])

    assert list(H.get([0])[0].edges(data=True)) == [(4, 6, {})]

def test_snapshotgraph_number_of_nodes():
    G = dnx.SnapshotGraph()
    G.add_snapshot([(1, 2), (1, 3)])
    G.add_snapshot([(1, 4), (1, 3)])

    assert G.number_of_nodes(sbunch=[1]) == [3]
    assert G.number_of_nodes(sbunch=[0, 1]) == [3, 3]

def test_snapshotgraph_order():
    G = dnx.SnapshotGraph()
    G.add_snapshot([(1, 2), (1, 3)])
    G.add_snapshot([(1, 4), (1, 3)])

    assert G.order([1]) == [3]
    assert G.order() == [3, 3]

def test_snapshotgraph_has_node():
    G = dnx.SnapshotGraph()
    G.add_snapshot([(1, 2), (1, 3)])
    G.add_snapshot([(1, 4), (1, 3)])
    assert G.has_node(1, [1]) == [True]
    assert G.has_node(1) == [True, True]

def test_snapshotgraph_is_multigraph():
    G = dnx.SnapshotGraph()
    G.add_snapshot([(1, 2), (1, 3)])
    G.add_snapshot([(1, 4), (1, 3)])
    assert G.is_multigraph([0, 1]) == [False, False]
    assert G.is_multigraph() == [False, False]

def test_snapshotgraph_is_directed():
    G = dnx.SnapshotGraph()
    G.add_snapshot([(1, 2), (1, 3)])
    G.add_snapshot([(1, 4), (1, 3)])
    assert G.is_directed([0, 1]) == [False, False]
    assert G.is_directed() == [False, False]

def test_snapshotgraph_to_directed():
    G = dnx.SnapshotGraph()
    G.add_snapshot([(1, 2), (1, 3)])
    G.add_snapshot([(1, 4), (1, 3)])

    assert isinstance(G.to_directed([0])[0], nx.classes.digraph.DiGraph)
    assert isinstance(G.to_directed()[1], nx.classes.digraph.DiGraph)

def test_snapshotgraph_to_undirected():
    G = dnx.SnapshotGraph()
    G.add_snapshot([(1, 2), (1, 3)])
    G.add_snapshot([(1, 4), (1, 3)])

    assert G.is_directed() == [False, False]

    assert isinstance(G.to_undirected([0])[0], nx.classes.graph.Graph)
    assert isinstance(G.to_undirected()[1], nx.classes.graph.Graph)

def test_snapshotgraph_size():
    G = dnx.SnapshotGraph()
    G.add_snapshot([(1, 2), (1, 3)])
    G.add_snapshot([(1, 4), (1, 3)])

    assert G.size([0]) == [2]
    assert G.size() == [2, 2]

def test_snapshotgraph_get():
    G = dnx.SnapshotGraph()
    nxG1 = nx.Graph()
    nxG2 = nx.Graph()
    nxG1.add_edges_from([(1, 2), (1, 3)])
    nxG2.add_edges_from([(1, 4), (1, 3)])
    G.add_snapshot(graph=nxG1)
    G.add_snapshot(graph=nxG2)

    assert G.get([0]) == [nxG1]
    assert G.get([1]) == [nxG2]
    assert G.get() == [nxG1, nxG2]

def test_add_nodes_from():
    G = dnx.SnapshotGraph()
    G.add_snapshot([(1, 2), (1, 3)])
    G.add_snapshot([(1, 4), (1, 3)])
    G.add_nodes_from([5, 6, 7], [0])
    G.add_nodes_from([8, 9, 10, 11], [1])

    assert {5, 6, 7}.issubset(set(G.get([0])[0].nodes()))
    assert {8, 9, 10, 11}.issubset(set(G.get([1])[0].nodes()))

def test_add_edges_from():
    G = dnx.SnapshotGraph()
    G.add_snapshot([(1, 2), (1, 3)])
    G.add_snapshot([(1, 4), (1, 3)])
    G.add_edges_from([(5, 6), (7, 6)], [0])
    G.add_edges_from([(8, 9), (10, 11)], [0, 1])

    assert {(5, 6), (6, 7)}.issubset(set(G.get([0])[0].edges()))
    assert {(8, 9), (10, 11)}.issubset(set(G.get([1])[0].edges()))

