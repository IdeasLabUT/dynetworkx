import dynetworkx as dnx
import networkx as nx
from networkx import from_numpy_matrix, from_numpy_array
import os
import numpy as np

current_dir = os.path.dirname(__file__)


def test_intervalgraph_degree():
    G = dnx.IntervalGraph()
    G.add_edge(1, 2, 3, 5)
    G.add_edge(2, 3, 8, 11)
    assert G.degree(2) == 2
    assert G.degree(2, 2) == 2
    assert G.degree(2, end=8) == 1
    assert G.degree() == 4 / 3
    assert G.degree(2, delta=True) == [(3, 1), (5, 0), (8, 1)]


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
    assert G.interval() == (10, 17)


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
    G.add_edge(3, 4, 5, 6)

    assert G.has_node(1)
    assert G.has_node(3, begin=2)
    assert G.has_node(3, end=2) == False


def test_intervalgraph_nodes_default():
    G = dnx.IntervalGraph()
    G.add_node(1)
    G.add_edge(3, 4, 5, 6)

    assert list(G.nodes()) == [1, 3, 4]


def test_intervalgraph_nodes_slice():
    G = dnx.IntervalGraph()
    G.add_edge(1, 2, 3, 4)
    G.add_edge(4, 5, 6, 7)
    G.add_edge(7, 8, 9, 10)

    assert sorted(list(G.nodes(begin=4))) == [4, 5, 7, 8]
    assert sorted(list(G.nodes(end=7))) == [1, 2, 4, 5]
    assert sorted(list(G.nodes(4, 7))) == [4, 5]


def test_intervalgraph_nodes_data():
    G = dnx.IntervalGraph()
    G.add_node(1, size=1.2)
    G.add_node(2)

    assert list(G.nodes(data=True)) == [(1, {'size': 1.2}), (2, {})]


def test_intervalgraph_remove_node_default():
    G = dnx.IntervalGraph()
    G.add_edges_from([(1, 2, 10, 11), (2, 4, 11, 12), (6, 4, 19, 20), (2, 4, 15, 16)])
    G.remove_node(6)
    assert list(G.nodes()) == [1, 2, 4]


def test_intervalgraph_remove_node_slice():
    G = dnx.IntervalGraph()
    G.add_edges_from([(1, 2, 10, 11), (2, 4, 11, 12), (6, 4, 19, 20), (2, 4, 15, 16)])
    assert G.has_node(2, begin=11) == True
    assert G.has_node(4, end=13) == True

    G.remove_node(2, begin=11)
    G.remove_node(4, end=13)

    assert list(G.nodes()) == [1, 2, 4, 6]
    assert G.has_node(2, begin=11) == False
    assert G.has_node(4, end=13) == False


def test_intervalgraph_add_edge():
    G = dnx.IntervalGraph()
    G.add_edge(1, 2, 3, 4)
    G.add_edge(1, 3, 4, 5, weight=7, capacity=15, length=342.7)

    assert list(G.edges(data=True)) == [((1, 2, 3, 4), {}), ((1, 3, 4, 5), {'capacity': 15, 'length': 342.7, 'weight': 7})]


def test_intervalgraph_add_edges_from():
    G = dnx.IntervalGraph()
    G.add_edges_from([(1, 2, 10, 11), (2, 4, 11, 12)])
    G.add_edges_from([(3, 4, 19, 20), (1, 4, 3, 4)], label='WN2898')

    assert list(G.edges(data=True)) == [((1, 4, 3, 4), {'label': 'WN2898'}), ((1, 2, 10, 11), {}),
                                        ((2, 4, 11, 12), {}), ((3, 4, 19, 20), {'label': 'WN2898'})]


def test_intervalgraph_has_edge():
    G = dnx.IntervalGraph()
    G.add_edges_from([(1, 2, 10, 11), (2, 4, 11, 12)])
    assert G.has_edge(1, 2)

    assert G.has_edge(1, 2, begin=2) == True
    assert G.has_edge(2, 4, begin=12) == False


def test_intervalgraph_edges_default():
    G = dnx.IntervalGraph()
    G.add_edge(3, 4, 5, 6)

    assert list(G.edges()) == [(3, 4, 5, 6)]


def test_intervalgraph_edges_slice():
    G = dnx.IntervalGraph()
    G.add_edges_from([(1, 2, 10, 11), (2, 4, 11, 12), (6, 4, 19, 20), (2, 4, 15, 16)])

    assert list(G.edges(begin=10)) == [(1, 2, 10, 11), (2, 4, 11, 12), (2, 4, 15, 16), (6, 4, 19, 20)]
    assert list(G.edges(end=11)) == [(1, 2, 10, 11)]
    assert list(G.edges(begin=11, end=15)) == [(2, 4, 11, 12)]
    assert list(G.edges(u=2)) == [(1, 2, 10, 11), (2, 4, 11, 12), (2, 4, 15, 16)]
    assert list(G.edges(v=2)) == [(1, 2, 10, 11), (2, 4, 11, 12), (2, 4, 15, 16)]
    assert list(G.edges(u=2, begin=11)) == [(2, 4, 11, 12), (2, 4, 15, 16)]
    assert list(G.edges(u=2, v=4, end=12)) == [(2, 4, 11, 12)]
    assert list(G.edges(u=1, v=2)) == [(1, 2, 10, 11)]


def test_intervalgraph_edges_data():
    G = dnx.IntervalGraph()
    G.add_edge(1, 3, 4, 5, weight=8, height=18)
    G.add_edge(1, 2, 10, 11, weight=10)
    G.add_edge(2, 6, 10, 11)

    assert list(G.edges(data="weight")) == [((1, 3, 4, 5), 8), ((1, 2, 10, 11), 10), ((2, 6, 10, 11), None)]
    assert list(G.edges(data="weight", default=5)) == [((1, 3, 4, 5), 8), ((1, 2, 10, 11), 10), ((2, 6, 10, 11), 5)]
    assert list(G.edges(data=True)) == [((1, 3, 4, 5), {'weight': 8, 'height': 18}),
                                        ((1, 2, 10, 11), {'weight': 10}), ((2, 6, 10, 11), {})]
    assert list(G.edges(u=1, begin=2, end=9, data="weight")) == [((1, 3, 4, 5), 8)]


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


def test_intervalgraph_from_networkx_graph_default():
    desired = dnx.IntervalGraph()
    desired.add_edge(1, 2, 10, 11, weight=1.5)
    desired.add_edge(2, 3, 11, 12)

    graph = nx.Graph()
    graph.add_edge(1, 2, begin=10, end=11, weight=1.5)
    graph.add_edge(2, 3, begin=11, end=12)

    actual = dnx.IntervalGraph.from_networkx_graph(graph)

    assert actual.edges(data=True) == desired.edges(data=True)


def test_intervalgraph_from_networkx_graph_timestamp():
    desired = dnx.IntervalGraph()
    desired.add_edge(1, 2, 10, 11, weight=1.5)
    desired.add_edge(2, 3, 11, 12)

    graph = nx.Graph()
    graph.add_edge(1, 2, custom_begin=10, custom_end=11, weight=1.5)
    graph.add_edge(2, 3, custom_begin=11, custom_end=12)

    actual = dnx.IntervalGraph.from_networkx_graph(graph, begin="custom_begin", end="custom_end")

    assert actual.edges(data=True) == desired.edges(data=True)


def test_intervalgraph_to_snapshot_graph():
    G = dnx.IntervalGraph()
    G.add_edges_from([(1, 2, 10, 11), (2, 4, 11, 12), (6, 4, 19, 20), (2, 4, 15, 16)])
    S, l = G.to_snapshot_graph(2, edge_interval_data=True, return_length=True)
    actual = []
    for g in S:
        actual.append(g.edges(data=True))
    assert list(actual[0]) == [(1, 2, {'begin': 10, 'end': 11}), (2, 4, {'begin': 11, 'end': 12})]
    assert list(actual[1]) == [(2, 4, {'begin': 15, 'end': 16}), (4, 6, {'begin': 19, 'end': 20})]


def test_intervalgraph_from_snapshots_default():
    desired = dnx.IntervalGraph()
    desired.add_edge(1, 2, 0, 1)
    desired.add_edge(1, 2, 2, 3)
    desired.add_edge(6, 7, 0, 1)
    desired.add_edge(5, 6, 0, 1)
    desired.add_edge(1, 4, 1, 2)
    desired.add_edge(1, 3, 0, 2)
    desired.add_edge(10, 11, 0, 2)
    desired.add_edge(8, 9, 0, 3, weight=1)

    sg = dnx.SnapshotGraph()
    sg.add_snapshot([(1, 2), (1, 3)], time=0)
    sg.add_snapshot([(1, 4), (1, 3)], time=1)
    sg.add_snapshot([(1, 2)], time=2)
    sg.add_edges_from([(5, 6), (7, 6)], [0])
    sg.add_edges_from([(8, 9), (10, 11)], [0, 1])
    sg.add_edges_from([(8, 9)], weight=1)

    actual = dnx.IntervalGraph.from_snapshot_graph(sg)

    assert len(actual.edges()) == len(desired.edges())
    for edge in actual.edges(data=True):
        assert edge in desired.edges(data=True)


def test_intervalgraph_from_snapshots_begin():
    desired = dnx.IntervalGraph()
    desired.add_edge(1, 2, 10, 11)
    desired.add_edge(6, 7, 10, 11)
    desired.add_edge(5, 6, 10, 11)
    desired.add_edge(1, 4, 11, 12)
    desired.add_edge(1, 3, 10, 12)
    desired.add_edge(10, 11, 10, 12)
    desired.add_edge(8, 9, 10, 12, weight=1)

    sg = dnx.SnapshotGraph()
    sg.add_snapshot([(1, 2), (1, 3)], time=0)
    sg.add_snapshot([(1, 4), (1, 3)], time=1)
    sg.add_edges_from([(5, 6), (7, 6)], [0])
    sg.add_edges_from([(8, 9), (10, 11)], [0, 1])
    sg.add_edges_from([(8, 9)], weight=1)

    actual = dnx.IntervalGraph.from_snapshot_graph(sg, begin=10)

    assert len(actual.edges()) == len(desired.edges())
    for edge in actual.edges(data=True):
        assert edge in desired.edges(data=True)


def test_intervalgraph_from_snapshots_period():
    desired = dnx.IntervalGraph()
    desired.add_edge(1, 2, 0, 2)
    desired.add_edge(6, 7, 0, 2)
    desired.add_edge(5, 6, 0, 2)
    desired.add_edge(1, 4, 2, 4)
    desired.add_edge(1, 3, 0, 4)
    desired.add_edge(10, 11, 0, 4)
    desired.add_edge(8, 9, 0, 4, weight=1)

    sg = dnx.SnapshotGraph()
    sg.add_snapshot([(1, 2), (1, 3)], time=0)
    sg.add_snapshot([(1, 4), (1, 3)], time=1)
    sg.add_edges_from([(5, 6), (7, 6)], [0])
    sg.add_edges_from([(8, 9), (10, 11)], [0, 1])
    sg.add_edges_from([(8, 9)], weight=1)

    actual = dnx.IntervalGraph.from_snapshot_graph(sg, period=2)

    assert len(actual.edges()) == len(desired.edges())
    for edge in actual.edges(data=True):
        assert edge in desired.edges(data=True)


def test_intervalgraph_to_snapshots_default():
    G = dnx.IntervalGraph()
    G.add_edges_from([(1, 2, 3, 6), (2, 4, 5, 11), (6, 4, 19, 20), (2, 4, 15, 16)])
    S = G.to_snapshots(2, return_length=True)

    assert len(S[0]) == 2
    assert S[1] == 8.5
    assert sorted(list(S[0][0].edges())) == [(1, 2), (2, 4)]
    assert sorted(list(S[0][1].edges())) == [(2, 4), (4, 6)]


def test_interval_graph_to_snapshots_len():
    G = dnx.IntervalGraph()
    G.add_edges_from([(1, 2, 3, 6), (2, 4, 5, 11), (6, 4, 19, 20), (2, 4, 15, 16)])
    S = G.to_snapshots(length_of_snapshots=2, return_length=True)

    assert len(S[0]) == 9
    assert S[1] == 2
    assert sorted(list(S[0][0].edges())) == [(1, 2)]
    assert sorted(list(S[0][1].edges())) == [(1, 2), (2, 4)]
    assert sorted(list(S[0][2].edges())) == [(2, 4)]
    assert sorted(list(S[0][3].edges())) == [(2, 4)]
    assert sorted(list(S[0][4].edges())) == []
    assert sorted(list(S[0][5].edges())) == []
    assert sorted(list(S[0][6].edges())) == [(2, 4)]
    assert sorted(list(S[0][7].edges())) == []
    assert sorted(list(S[0][8].edges())) == [(6, 4)]


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
    assert isinstance(H, nx.classes.graph.Graph)


def test_intervalgraph_to_subgraph_node_data():
    G = dnx.IntervalGraph()
    G.add_node(1, size=1.2)
    G.add_edges_from([(1, 2, 3, 6), (2, 4, 5, 11), (6, 4, 19, 20), (2, 4, 15, 16)])
    H = G.to_subgraph(4, 12, node_data=True)

    assert list(H.edges()) == [(1, 2), (2, 4)]
    assert list(H.nodes(data=True)) == [(1, {'size': 1.2}), (2, {}), (4, {})]
    assert isinstance(H, nx.classes.graph.Graph)


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


def test_intervalgraph_load_from_text_default():
    path = os.path.join(current_dir, 'inputoutput_text/intervalgraph_load_from_text_default.txt')
    desired = dnx.IntervalGraph()
    desired.add_edge(1, 2, 3.0, 4.0)
    desired.add_edge(5, 6, 7.0, 8.0)
    desired.add_edge(9, 10, 11.0, 12.0, weight=1.0)
    desired.add_edge(13, 14, 15.0, 16.0, weight=2.0)

    actual = dnx.IntervalGraph.load_from_txt(path)

    assert actual.edges(data=True) == desired.edges(data=True)


def test_intervalgraph_load_from_text_delimiter():
    path = os.path.join(current_dir, 'inputoutput_text/intervalgraph_load_from_text_delimiter.txt')
    desired = dnx.IntervalGraph()
    desired.add_edge(1, 2, 3.0, 4.0)
    desired.add_edge(5, 6, 7.0, 8.0)
    desired.add_edge(9, 10, 11.0, 12.0, weight=1.0)
    desired.add_edge(13, 14, 15.0, 16.0, weight=2.0)

    actual = dnx.IntervalGraph.load_from_txt(path, delimiter='\t')

    assert actual.edges(data=True) == desired.edges(data=True)


def test_intervalgraph_load_from_text_inputtypes():
    path = os.path.join(current_dir, 'inputoutput_text/intervalgraph_load_from_text_default.txt')
    desired = dnx.IntervalGraph()
    desired.add_edge('1', '2', 3.0, 4.0)
    desired.add_edge('5', '6', 7.0, 8.0)
    desired.add_edge('9', '10', 11.0, 12.0, weight=1.0)
    desired.add_edge('13', '14', 15.0, 16.0, weight=2.0)

    actual = dnx.IntervalGraph.load_from_txt(path, nodetype=str, intervaltype=float)

    assert actual.edges(data=True) == desired.edges(data=True)


def test_intervalgraph_load_from_text_comments():
    path = os.path.join(current_dir, 'inputoutput_text/intervalgraph_load_from_text_comments.txt')
    desired = dnx.IntervalGraph()
    desired.add_edge(1, 2, 3, 4.0)
    desired.add_edge(5, 6, 7, 8.0)
    desired.add_edge(9, 10, 11, 12.0, weight=1.0)
    desired.add_edge(13, 14, 15, 16.0, weight=2.0)

    actual = dnx.IntervalGraph.load_from_txt(path, comments='@')

    assert actual.edges(data=True) == desired.edges(data=True)


def test_intervalgraph_save_to_text_default():
    input_path = os.path.join(current_dir, 'inputoutput_text/intervalgraph_save_to_text_default.txt')
    output_path = os.path.join(current_dir, 'inputoutput_text/intervalgraph_save_to_text_default_test.txt')

    G = dnx.IntervalGraph()
    G.add_edge(1, 2, 3, 4.0)
    G.add_edge(5, 6, 7, 8.0)
    G.add_edge(9, 10, 11, 12.0, weight=1.0)
    G.add_edge(13, 14, 15, 16.0, weight=2.0)

    G.save_to_txt(output_path)

    with open(input_path, 'r') as input_file:
        desired = input_file.read()
    with open(output_path, 'r') as output_file:
        actual = output_file.read()

    assert actual == desired


def test_intervalgraph_save_to_text_delimiter():
    input_path = os.path.join(current_dir, 'inputoutput_text/intervalgraph_save_to_text_delimiter.txt')
    output_path = os.path.join(current_dir, 'inputoutput_text/intervalgraph_save_to_text_delimiter_test.txt')

    G = dnx.IntervalGraph()
    G.add_edge(1, 2, 3, 4.0)
    G.add_edge(5, 6, 7, 8.0)
    G.add_edge(9, 10, 11, 12.0, weight=1.0)
    G.add_edge(13, 14, 15, 16.0, weight=2.0)

    G.save_to_txt(output_path, delimiter='\t')

    with open(input_path, 'r') as input_file:
        desired = input_file.read()
    with open(output_path, 'r') as output_file:
        actual = output_file.read()

    assert actual == desired
