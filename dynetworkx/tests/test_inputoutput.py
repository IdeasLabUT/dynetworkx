import dynetworkx as dnx
import os
import numpy as np
from networkx import from_numpy_matrix, from_numpy_array
current_dir = os.path.dirname(__file__)

def test_impulsegraph_load_from_text_default():

    path = os.path.join(current_dir,'inputoutput_text/impulsegraph_load_from_text_default.txt')
    desired = dnx.ImpulseGraph()
    desired.add_edge(1,2,3.0)
    desired.add_edge(2,3,4.0)
    desired.add_edge(3,4,5.0,weight=1.0)
    desired.add_edge(6,7,8.0,weight=2)

    actual = dnx.ImpulseGraph.load_from_txt(path)

    assert actual.edges(data=True) == desired.edges(data=True)

def test_impulsegraph_load_from_text_delimiter():

    path = os.path.join(current_dir,'inputoutput_text/impulsegraph_load_from_text_delimiter.txt')
    desired = dnx.ImpulseGraph()
    desired.add_edge(1,2,3.0)
    desired.add_edge(2,3,4.0)
    desired.add_edge(3,4,5.0,weight=1.0)
    desired.add_edge(6,7,8.0,weight=2)

    actual = dnx.ImpulseGraph.load_from_txt(path,delimiter='\t')

    assert actual.edges(data=True) == desired.edges(data=True)

def test_impulsegraph_load_from_text_inputtypes():

    path = os.path.join(current_dir,'inputoutput_text/impulsegraph_load_from_text_default.txt')
    desired = dnx.ImpulseGraph()
    desired.add_edge(1,2,3.0)
    desired.add_edge(2,3,4.0)
    desired.add_edge(3,4,5.0,weight=1)
    desired.add_edge(6,7,8.0,weight=2)

    actual = dnx.ImpulseGraph.load_from_txt(path,nodetype=int,timestamptype=float)

    assert actual.edges(data=True) == desired.edges(data=True)

def test_impulsegraph_load_from_text_comments():
    path = os.path.join(current_dir,'inputoutput_text/impulsegraph_load_from_text_comments.txt')
    desired = dnx.ImpulseGraph()
    desired.add_edge(1,2,3.0)
    desired.add_edge(2,3,4.0)
    desired.add_edge(3,4,5.0,weight=1.0)
    desired.add_edge(6,7,8.0,weight=2.0)

    actual = dnx.ImpulseGraph.load_from_txt(path,comments='@')

    assert actual.edges(data=True) == desired.edges(data=True)

def test_impulsegraph_save_to_text_default():

    input_path = os.path.join(current_dir,'inputoutput_text/impulsegraph_save_to_text_default.txt')
    output_path = os.path.join(current_dir,'inputoutput_text/impulsegraph_save_to_text_default_test.txt')

    G = dnx.ImpulseGraph()
    G.add_edge(1,2,3.0)
    G.add_edge(2,3,4.0)
    G.add_edge(3,4,5.0,weight=1.0)
    G.add_edge(6,7,8.0,weight=2.0)

    G.save_to_txt(output_path)

    with open(input_path,'r') as input_file:
        desired = input_file.read()
    with open(output_path,'r') as output_file:
        actual = output_file.read()

    assert actual == desired

def test_impulsegraph_save_to_text_delimiter():

    input_path = os.path.join(current_dir,'inputoutput_text/impulsegraph_save_to_text_delimiter.txt')
    output_path = os.path.join(current_dir,'inputoutput_text/impulsegraph_save_to_text_delimiter_test.txt')

    G = dnx.ImpulseGraph()
    G.add_edge(1,2,3.0)
    G.add_edge(2,3,4.0)
    G.add_edge(3,4,5.0,weight=1.0)
    G.add_edge(6,7,8.0,weight=2.0)

    G.save_to_txt(output_path,delimiter='\t')

    with open(input_path,'r') as input_file:
        desired = input_file.read()
    with open(output_path,'r') as output_file:
        actual = output_file.read()

    assert actual == desired

def test_intervalgraph_load_from_text_default():

    path = os.path.join(current_dir,'inputoutput_text/intervalgraph_load_from_text_default.txt')
    desired = dnx.IntervalGraph()
    desired.add_edge(1,2,3.0,4.0)
    desired.add_edge(5,6,7.0,8.0)
    desired.add_edge(9,10,11.0,12.0,weight=1.0)
    desired.add_edge(13,14,15.0,16.0,weight=2.0)

    actual = dnx.IntervalGraph.load_from_txt(path)

    assert actual.edges(data=True) == desired.edges(data=True)

def test_intervalgraph_load_from_text_delimiter():

    path = os.path.join(current_dir,'inputoutput_text/intervalgraph_load_from_text_delimiter.txt')
    desired = dnx.IntervalGraph()
    desired.add_edge(1,2,3.0,4.0)
    desired.add_edge(5,6,7.0,8.0)
    desired.add_edge(9,10,11.0,12.0,weight=1.0)
    desired.add_edge(13,14,15.0,16.0,weight=2.0)

    actual = dnx.IntervalGraph.load_from_txt(path,delimiter='\t')

    assert actual.edges(data=True) == desired.edges(data=True)

def test_intervalgraph_load_from_text_inputtypes():

    path = os.path.join(current_dir,'inputoutput_text/intervalgraph_load_from_text_default.txt')
    desired = dnx.IntervalGraph()
    desired.add_edge('1','2','3.0','4.0')
    desired.add_edge('5','6','7.0','8.0')
    desired.add_edge('9','10','11.0','12.0',weight=1.0)
    desired.add_edge('13','14','15.0','16.0',weight=2.0)

    actual = dnx.IntervalGraph.load_from_txt(path,nodetype=str,intervaltype=str)

    assert actual.edges(data=True) == desired.edges(data=True)

def test_intervalgraph_load_from_text_comments():
    path = os.path.join(current_dir,'inputoutput_text/intervalgraph_load_from_text_comments.txt')
    desired = dnx.IntervalGraph()
    desired.add_edge(1,2,3,4.0)
    desired.add_edge(5,6,7,8.0)
    desired.add_edge(9,10,11,12.0,weight=1.0)
    desired.add_edge(13,14,15,16.0,weight=2.0)

    actual = dnx.IntervalGraph.load_from_txt(path,comments='@')

    assert actual.edges(data=True) == desired.edges(data=True)

def test_intervalgraph_save_to_text_default():

    input_path = os.path.join(current_dir,'inputoutput_text/intervalgraph_save_to_text_default.txt')
    output_path = os.path.join(current_dir,'inputoutput_text/intervalgraph_save_to_text_default_test.txt')

    G = dnx.IntervalGraph()
    G.add_edge(1,2,3,4.0)
    G.add_edge(5,6,7,8.0)
    G.add_edge(9,10,11,12.0,weight=1.0)
    G.add_edge(13,14,15,16.0,weight=2.0)

    G.save_to_txt(output_path)

    with open(input_path,'r') as input_file:
        desired = input_file.read()
    with open(output_path,'r') as output_file:
        actual = output_file.read()

    assert actual == desired

def test_intervalgraph_save_to_text_delimiter():

    input_path = os.path.join(current_dir,'inputoutput_text/intervalgraph_save_to_text_delimiter.txt')
    output_path = os.path.join(current_dir,'inputoutput_text/intervalgraph_save_to_text_delimiter_test.txt')

    G = dnx.IntervalGraph()
    G.add_edge(1,2,3,4.0)
    G.add_edge(5,6,7,8.0)
    G.add_edge(9,10,11,12.0,weight=1.0)
    G.add_edge(13,14,15,16.0,weight=2.0)

    G.save_to_txt(output_path,delimiter='\t')

    with open(input_path,'r') as input_file:
        desired = input_file.read()
    with open(output_path,'r') as output_file:
        actual = output_file.read()

    assert actual == desired

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