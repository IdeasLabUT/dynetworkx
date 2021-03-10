import dynetworkx as dnx
import networkx as nx
from networkx import from_numpy_matrix, from_numpy_array
import os
import numpy as np

current_dir = os.path.dirname(__file__)


def test_impulsegraph_degree():
    G = dnx.ImpulseGraph()
    G.add_edge(1, 2, 3)
    G.add_edge(2, 3, 8)
    assert G.degree(2) == 2
    assert G.degree(2, 2) == 2
    assert G.degree(2, end=8, inclusive=(True, False)) == 1
    assert G.degree() == 4 / 3
    assert G.degree(2, delta=True) == [(3, 1), (8, 1)]


def test_impulsegraph_init_default():
    G = dnx.ImpulseGraph()
    assert G.graph == {}
    assert G._node == {}
    assert G._adj == {}
    assert G.name == ''


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
    G.add_nodes_from([0, 1, 2])
    assert len(G) == 3


def test_impulsegraph_contains():
    G = dnx.ImpulseGraph()
    G.add_node(2)
    assert 2 in G


def test_impulsegraph_interval():
    G = dnx.ImpulseGraph()
    G.add_edges_from([(1, 2, 10), (3, 7, 16)])
    assert G.interval() == (10, 16)


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
    assert G.number_of_nodes(end=11) == 2


def test_impulsegraph_has_node():
    G = dnx.ImpulseGraph()
    G.add_node(1)
    G.add_edge(3, 4, 5)

    assert G.has_node(1)
    assert G.has_node(3, begin=2)
    assert G.has_node(3, end=2) == False


def test_impulsegraph_nodes_default():
    G = dnx.ImpulseGraph()
    G.add_node(1)
    G.add_edge(3, 4, 5)

    assert list(G.nodes()) == [1, 3, 4]


def test_impulsegraph_nodes_slice():
    G = dnx.ImpulseGraph()
    G.add_edge(1, 2, 3)
    G.add_edge(4, 5, 6)
    G.add_edge(7, 8, 9)

    assert sorted(list(G.nodes(begin=4))) == [4, 5, 7, 8]
    assert sorted(list(G.nodes(end=7))) == [1, 2, 4, 5]
    assert sorted(list(G.nodes(4, 7))) == [4, 5]


def test_impulsegraph_nodes_data():
    G = dnx.ImpulseGraph()
    G.add_node(1, size=1.2)
    G.add_node(2)

    assert list(G.nodes(data=True)) == [(1, {'size': 1.2}), (2, {})]


def test_impulsegraph_remove_node_default():
    G = dnx.ImpulseGraph()
    G.add_edges_from([(1, 2, 10), (2, 4, 11), (6, 4, 19), (2, 4, 15)])
    G.remove_node(6)
    assert list(G.nodes()) == [1, 2, 4]


def test_impulsegraph_remove_node_slice():
    G = dnx.ImpulseGraph()
    G.add_edges_from([(1, 2, 10), (2, 4, 11), (6, 4, 19), (2, 4, 15)])
    assert G.has_node(2, begin=11) == True
    assert G.has_node(4, end=13) == True

    G.remove_node(2, begin=11)
    G.remove_node(4, end=13)

    assert list(G.nodes()) == [1, 2, 4, 6]
    assert G.has_node(2, begin=11) == False
    assert G.has_node(4, end=13) == False


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
    G.add_edge(3, 4, 5)

    assert list(G.edges()) == [(3, 4, 5)]


def test_impulsegraph_edges_slice():
    G = dnx.ImpulseGraph()
    G.add_edges_from([(1, 2, 10), (2, 4, 11), (6, 4, 19), (2, 4, 15)])

    assert list(G.edges(begin=10)) == [(1, 2, 10), (2, 4, 11), (2, 4, 15), (6, 4, 19)]
    assert list(G.edges(end=12)) == [(1, 2, 10), (2, 4, 11)]
    assert list(G.edges(begin=11, end=16)) == [(2, 4, 11), (2, 4, 15)]
    assert list(G.edges(u=2)) == [(1, 2, 10), (2, 4, 11), (2, 4, 15)]
    assert list(G.edges(v=2)) == [(1, 2, 10), (2, 4, 11), (2, 4, 15)]
    assert list(G.edges(u=2, begin=11)) == [(2, 4, 11), (2, 4, 15)]
    assert list(G.edges(u=2, v=4, end=12)) == [(2, 4, 11)]
    assert list(G.edges(u=1, v=2)) == [(1, 2, 10)]


def test_impulsegraph_edges_data():
    G = dnx.ImpulseGraph()
    G.add_edge(1, 3, 4, weight=8, height=18)
    G.add_edge(1, 2, 10, weight=10)
    G.add_edge(2, 6, 10)

    assert list(G.edges(data="weight")) == [((1, 3, 4), 8), ((1, 2, 10), 10), ((2, 6, 10), None)]
    assert list(G.edges(data="weight", default=5)) == [((1, 3, 4), 8), ((1, 2, 10), 10), ((2, 6, 10), 5)]
    assert list(G.edges(data=True)) == [((1, 3, 4), {'weight': 8, 'height': 18}), ((1, 2, 10), {'weight': 10}),
                                        ((2, 6, 10), {})]
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


def test_impulsegraph_from_networkx_graph_default():
    desired = dnx.ImpulseGraph()
    desired.add_edge(1, 2, 10, weight=1.5)
    desired.add_edge(2, 3, 11)

    graph = nx.Graph()
    graph.add_edge(1, 2, timestamp=10, weight=1.5)
    graph.add_edge(2, 3, timestamp=11)

    actual = dnx.ImpulseGraph.from_networkx_graph(graph)

    assert actual.edges(data=True) == desired.edges(data=True)


def test_impulsegraph_from_networkx_graph_timestamp():
    desired = dnx.ImpulseGraph()
    desired.add_edge(1, 2, 10, weight=1.5)
    desired.add_edge(2, 3, 11)

    graph = nx.Graph()
    graph.add_edge(1, 2, custom=10, weight=1.5)
    graph.add_edge(2, 3, custom=11)

    actual = dnx.ImpulseGraph.from_networkx_graph(graph, timestamp="custom")

    assert actual.edges(data=True) == desired.edges(data=True)


def test_impulsegraph_to_snapshots_default():
    G = dnx.ImpulseGraph()
    G.add_edges_from([(1, 2, 10), (2, 4, 11), (6, 4, 19), (2, 4, 15)])
    S = G.to_snapshots(2)

    n1 = nx.Graph()
    n1.add_edge(1, 2, timestamp=10)
    n1.add_edge(2, 4, timestamp=11)

    n2 = nx.Graph()
    n2.add_edge(2, 4, timestamp=15)
    n2.add_edge(4, 6, timestamp=19)

    nl = [n1, n2]

    for i in range(len(S)):
        assert list(S[i].edges()) == list(nl[i].edges())


def test_impulsegraph_to_snapshots_len():
    G = dnx.ImpulseGraph()
    G.add_edges_from([(1, 2, 3), (2, 4, 5), (6, 4, 20), (2, 4, 15)])
    S = G.to_snapshots(length_of_snapshots=2, return_length=True)

    assert len(S[0]) == 9
    assert S[1] == 2
    assert sorted(list(S[0][0].edges())) == [(1, 2)]
    assert sorted(list(S[0][1].edges())) == [(2, 4)]
    assert sorted(list(S[0][2].edges())) == []
    assert sorted(list(S[0][3].edges())) == []
    assert sorted(list(S[0][4].edges())) == []
    assert sorted(list(S[0][5].edges())) == []
    assert sorted(list(S[0][6].edges())) == [(2, 4)]
    assert sorted(list(S[0][7].edges())) == []
    assert sorted(list(S[0][8].edges())) == [(6, 4)]


def test_impulsegraph_to_snapshots_multigraph():
    G = dnx.ImpulseGraph()
    G.add_edges_from([(1, 2, 10), (1, 2, 11), (6, 4, 19), (2, 4, 15)])
    S = G.to_snapshots(2, edge_timestamp_data=True, multigraph=True)

    n1 = nx.MultiGraph()
    n1.add_edge(1, 2, timestamp=10)
    n1.add_edge(1, 2, timestamp=11)

    n2 = nx.MultiGraph()
    n2.add_edge(2, 4, timestamp=15)
    n2.add_edge(4, 6, timestamp=19)

    nl = [n1, n2]

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

    nl = [n1, n2]

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

    nl = [n1, n2]

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

    nl = [n1, n2]

    for i in range(len(S)):
        assert list(S[i].edges(data=True)) == list(nl[i].edges(data=True))
        assert list(S[i].nodes(data=True)) == list(nl[i].nodes(data=True))


def test_impulsegraph_to_subgraph_default():
    G = dnx.ImpulseGraph()
    G.add_edges_from([(1, 2, 10), (2, 4, 11), (6, 4, 19), (2, 4, 15)])
    H = G.to_subgraph(4, 12)

    assert list(H.edges(data=True)) == [(1, 2, {}), (2, 4, {})]
    assert isinstance(H, nx.classes.graph.Graph)


def test_impulsegraph_to_subgraph_edge_data():
    G = dnx.ImpulseGraph()
    G.add_edges_from([(1, 2, 10), (2, 4, 11), (6, 4, 19), (2, 4, 15)], weight=1.5)
    H = G.to_subgraph(4, 12, edge_data=True)

    assert list(H.edges(data=True)) == [(1, 2, {'weight': 1.5}), (2, 4, {'weight': 1.5})]
    assert isinstance(H, nx.classes.graph.Graph)


def test_impulsegraph_to_subgraph_node_data():
    G = dnx.ImpulseGraph()
    G.add_node(1, size=1.2)
    G.add_edges_from([(1, 2, 10), (2, 4, 11), (6, 4, 19), (2, 4, 15)])
    H = G.to_subgraph(4, 12, node_data=True)

    assert list(H.edges(data=True)) == [(1, 2, {}), (2, 4, {})]
    assert list(H.nodes(data=True)) == [(1, {'size': 1.2}), (2, {}), (4, {})]
    assert isinstance(H, nx.classes.graph.Graph)


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


def test_impulsegraph_to_snapshot_graph():
    G = dnx.ImpulseGraph()
    G.add_edge(1, 2, 10)
    G.add_edge(2, 3, 11)
    G.add_edge(2, 4, 11)
    G.add_edge(4, 6, 19)
    S = G.to_snapshot_graph()

    n1 = nx.Graph()
    n1.add_edge(1, 2)

    n2 = nx.Graph()
    n2.add_edge(2, 3)
    n2.add_edge(2, 4)

    n3 = nx.Graph()
    n3.add_edge(4, 6)

    nl = [n1, n2, n3]

    for i in range(len(S)):
        assert list(S.snapshots.values()[i].edges(data=True)) == list(nl[i].edges(data=True))


def test_impulsegraph_load_from_text_default():
    path = os.path.join(current_dir, 'inputoutput_text/impulsegraph_load_from_text_default.txt')
    desired = dnx.ImpulseGraph()
    desired.add_edge(1, 2, 3.0)
    desired.add_edge(2, 3, 4.0)
    desired.add_edge(3, 4, 5.0, weight=1.0)
    desired.add_edge(6, 7, 8.0, weight=2)

    actual = dnx.ImpulseGraph.load_from_txt(path)

    assert actual.edges(data=True) == desired.edges(data=True)


def test_impulsegraph_load_from_text_delimiter():
    path = os.path.join(current_dir, 'inputoutput_text/impulsegraph_load_from_text_delimiter.txt')
    desired = dnx.ImpulseGraph()
    desired.add_edge(1, 2, 3.0)
    desired.add_edge(2, 3, 4.0)
    desired.add_edge(3, 4, 5.0, weight=1.0)
    desired.add_edge(6, 7, 8.0, weight=2)

    actual = dnx.ImpulseGraph.load_from_txt(path, delimiter='\t')

    assert actual.edges(data=True) == desired.edges(data=True)


def test_impulsegraph_load_from_text_inputtypes():
    path = os.path.join(current_dir, 'inputoutput_text/impulsegraph_load_from_text_default.txt')
    desired = dnx.ImpulseGraph()
    desired.add_edge(1, 2, 3.0)
    desired.add_edge(2, 3, 4.0)
    desired.add_edge(3, 4, 5.0, weight=1)
    desired.add_edge(6, 7, 8.0, weight=2)

    actual = dnx.ImpulseGraph.load_from_txt(path, nodetype=int, timestamptype=float)

    assert actual.edges(data=True) == desired.edges(data=True)


def test_impulsegraph_load_from_text_comments():
    path = os.path.join(current_dir, 'inputoutput_text/impulsegraph_load_from_text_comments.txt')
    desired = dnx.ImpulseGraph()
    desired.add_edge(1, 2, 3.0)
    desired.add_edge(2, 3, 4.0)
    desired.add_edge(3, 4, 5.0, weight=1.0)
    desired.add_edge(6, 7, 8.0, weight=2.0)

    actual = dnx.ImpulseGraph.load_from_txt(path, comments='@')

    assert actual.edges(data=True) == desired.edges(data=True)


def test_impulsegraph_save_to_text_default():
    input_path = os.path.join(current_dir, 'inputoutput_text/impulsegraph_save_to_text_default.txt')
    output_path = os.path.join(current_dir, 'inputoutput_text/impulsegraph_save_to_text_default_test.txt')

    G = dnx.ImpulseGraph()
    G.add_edge(1, 2, 3.0)
    G.add_edge(2, 3, 4.0)
    G.add_edge(3, 4, 5.0, weight=1.0)
    G.add_edge(6, 7, 8.0, weight=2.0)

    G.save_to_txt(output_path)

    with open(input_path, 'r') as input_file:
        desired = input_file.read()
    with open(output_path, 'r') as output_file:
        actual = output_file.read()

    assert actual == desired


def test_impulsegraph_save_to_text_delimiter():
    input_path = os.path.join(current_dir, 'inputoutput_text/impulsegraph_save_to_text_delimiter.txt')
    output_path = os.path.join(current_dir, 'inputoutput_text/impulsegraph_save_to_text_delimiter_test.txt')

    G = dnx.ImpulseGraph()
    G.add_edge(1, 2, 3.0)
    G.add_edge(2, 3, 4.0)
    G.add_edge(3, 4, 5.0, weight=1.0)
    G.add_edge(6, 7, 8.0, weight=2.0)

    G.save_to_txt(output_path, delimiter='\t')

    with open(input_path, 'r') as input_file:
        desired = input_file.read()
    with open(output_path, 'r') as output_file:
        actual = output_file.read()

    assert actual == desired
