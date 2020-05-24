import dynetworkx as dnx
import networkx as nx
from intervaltree import Interval
from networkx import from_numpy_matrix, from_numpy_array
import os
import numpy as np
current_dir = os.path.dirname(__file__)

def test_snapshotgraph_degree():
    G = dnx.SnapshotGraph()
    G.add_snapshot([(1, 2), (1, 3)])
    G.add_snapshot([(1, 4), (1, 3)])
    assert list(G.degree([1])[0]) == [(1, 2), (4, 1), (3, 1)]
    assert [list(G.degree(nbunch=[1, 2])[0]), list(G.degree(nbunch=[1, 2])[1])] == [[(1, 2), (2, 1)], [(1, 2)]]

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

def test_snapshotgraph_add_nodes_from():
    G = dnx.SnapshotGraph()
    G.add_snapshot([(1, 2), (1, 3)])
    G.add_snapshot([(1, 4), (1, 3)])
    G.add_nodes_from([5, 6, 7], [0])
    G.add_nodes_from([8, 9, 10, 11], [1])

    assert {5, 6, 7}.issubset(set(G.get([0])[0].nodes()))
    assert {8, 9, 10, 11}.issubset(set(G.get([1])[0].nodes()))

def test_snapshotgraph_add_edges_from():
    G = dnx.SnapshotGraph()
    G.add_snapshot([(1, 2), (1, 3)])
    G.add_snapshot([(1, 4), (1, 3)])
    G.add_edges_from([(5, 6), (7, 6)], [0])
    G.add_edges_from([(8, 9), (10, 11)], [0, 1])

    assert {(5, 6), (6, 7)}.issubset(set(G.get([0])[0].edges()))
    assert {(8, 9), (10, 11)}.issubset(set(G.get([1])[0].edges()))

def test_snapshotgraph_load_from_text_default():

    path = os.path.join(current_dir,'inputoutput_text/snapshotgraph_load_from_text_default.txt')
    desired = dnx.SnapshotGraph()
    desired.insert(from_numpy_array(
        np.array([[0,1,1,0,0,0,0],[1,0,0,0,0,0,0],[1,0,0,0,0,0,0],[0,0,0,0,1,0,0],[0,0,0,1,0,0,0],[0,0,0,0,0,0,1],[0,0,0,0,0,1,0]])))

    actual = dnx.SnapshotGraph.load_from_txt(path)

    for i in range(max(len(actual.get()),len(desired.get()))):
        assert list(desired.get()[i].edges(data=True)) == list(desired.get()[i].edges(data=True))

def test_snapshotgraph_load_from_text_delimiter():

    path = os.path.join(current_dir,'inputoutput_text/snapshotgraph_load_from_text_delimiter.txt')
    desired = dnx.SnapshotGraph()
    desired.insert(from_numpy_array(
        np.array([[0,1,1,0,0,0,0],[1,0,0,0,0,0,0],[1,0,0,0,0,0,0],[0,0,0,0,1,0,0],[0,0,0,1,0,0,0],[0,0,0,0,0,0,1],[0,0,0,0,0,1,0]])))

    actual = dnx.SnapshotGraph.load_from_txt(path,delimiter='|')

    for i in range(max(len(actual.get()),len(desired.get()))):
        assert list(desired.get()[i].edges(data=True)) == list(desired.get()[i].edges(data=True))

def test_snapshotgraph_load_from_text_comments():

    path = os.path.join(current_dir,'inputoutput_text/snapshotgraph_load_from_text_comments.txt')
    desired = dnx.SnapshotGraph()
    desired.insert(from_numpy_array(
        np.array([[0,1,1,0,0,0,0],[1,0,0,0,0,0,0],[1,0,0,0,0,0,0],[0,0,0,0,1,0,0],[0,0,0,1,0,0,0],[0,0,0,0,0,0,1],[0,0,0,0,0,1,0]])))

    actual = dnx.SnapshotGraph.load_from_txt(path,comments='@')

    for i in range(max(len(actual.get()),len(desired.get()))):
        assert list(desired.get()[i].edges(data=True)) == list(desired.get()[i].edges(data=True))

def test_snapshotgraph_load_from_text_multi():

    path = os.path.join(current_dir,'inputoutput_text/snapshotgraph_load_from_text_multi.txt')
    desired = dnx.SnapshotGraph()
    desired.insert(from_numpy_array(
        np.array([[0,1,1,0,0,0,0],[1,0,0,0,0,0,0],[1,0,0,0,0,0,0],[0,0,0,0,1,0,0],[0,0,0,1,0,0,0],[0,0,0,0,0,0,1],[0,0,0,0,0,1,0]])))
    desired.insert(from_numpy_matrix(
        np.array([[0,1,1,0,0,0,0],[1,0,0,0,0,0,0],[1,0,0,0,0,0,0],[0,0,0,0,1,0,0],[0,0,0,1,0,0,0],[0,0,0,0,0,0,1],[0,0,0,0,0,1,0]])))

    actual = dnx.SnapshotGraph.load_from_txt(path)

    for i in range(max(len(actual.get()),len(desired.get()))):
        assert list(desired.get()[i].edges(data=True)) == list(desired.get()[i].edges(data=True))

def test_snapshotgraph_save_to_text_default():

    input_path = os.path.join(current_dir,'inputoutput_text/snapshotgraph_save_to_text_default.txt')
    output_path = os.path.join(current_dir,'inputoutput_text/snapshotgraph_save_to_text_default_test.txt')

    G = dnx.SnapshotGraph()
    G.insert(from_numpy_array(
        np.array([[0,1,1,0,0,0,0],[1,0,0,0,0,0,0],[1,0,0,0,0,0,0],[0,0,0,0,1,0,0],[0,0,0,1,0,0,0],[0,0,0,0,0,0,1],[0,0,0,0,0,1,0]])))
    G.insert(from_numpy_array(
        np.array([[0,1,1,0,0,0,0],[1,0,0,0,0,0,0],[1,0,0,0,0,0,0],[0,0,0,0,1,0,0],[0,0,0,1,0,0,0],[0,0,0,0,0,0,1],[0,0,0,0,0,1,0]])))

    G.save_to_txt(output_path)

    with open(input_path,'r') as input_file:
        desired = input_file.read()
    with open(output_path,'r') as output_file:
        actual = output_file.read()

    assert actual == desired

def test_snapshotgraph_save_to_text_delimiter():

    input_path = os.path.join(current_dir,'inputoutput_text/snapshotgraph_save_to_text_delimiter.txt')
    output_path = os.path.join(current_dir,'inputoutput_text/snapshotgraph_save_to_text_delimiter_test.txt')

    G = dnx.SnapshotGraph()
    G.insert(from_numpy_array(
        np.array([[0,1,1,0,0,0,0],[1,0,0,0,0,0,0],[1,0,0,0,0,0,0],[0,0,0,0,1,0,0],[0,0,0,1,0,0,0],[0,0,0,0,0,0,1],[0,0,0,0,0,1,0]])))
    G.insert(from_numpy_array(
        np.array([[0,1,1,0,0,0,0],[1,0,0,0,0,0,0],[1,0,0,0,0,0,0],[0,0,0,0,1,0,0],[0,0,0,1,0,0,0],[0,0,0,0,0,0,1],[0,0,0,0,0,1,0]])))

    G.save_to_txt(output_path,delimiter='|')

    with open(input_path,'r') as input_file:
        desired = input_file.read()
    with open(output_path,'r') as output_file:
        actual = output_file.read()

    assert actual == desired
