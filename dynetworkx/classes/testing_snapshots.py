from snapshotgraph import SnapshotGraph
import os, glob
import numpy as np
import networkx as nx


def clean_data(filepath):
    for file_name in glob.glob(filepath + "*.csv"):
        if "_clean" not in file_name:
            file = open(file_name, "r")
            temp_str = file.read()

            temp_str = temp_str.replace("  ", " ")
            temp_str = temp_str.replace("\n ", "\n")

            file_new = open(file_name[:-4] + "_clean.csv", "w")
            file_new.write(temp_str[1:]) # only moves over the first column

            file.close()
            file_new.close()


def load_data(filepath):
    snapshots = []
    for file in glob.glob(filepath + "*_clean.csv"):
        snapshots.append(np.loadtxt(file, delimiter=" "))

    return snapshots


data_path = "/nethome/msloma/Newfrat/newfrat/"
#clean_data(data_path)
snaps = load_data(data_path)

graphs = []
for val in snaps:
    G = nx.from_numpy_matrix(val)
    graphs.append(G)

snap_graph = SnapshotGraph(name="NewFrat")
for g in graphs:
    snap_graph.add_snapshot(g.edges(data=True))

# set and read name of graph
print(snap_graph.name)
print(snap_graph)

# Length
print("len: {}".format(len(snap_graph)))

# contains
print("contains: {}".format(2 in snap_graph))

# insert
snap_graph.insert(graphs[1], snap_len=1, num_in_seq=40)

# add snapshot
snap_graph.add_snapshot(graphs[len(graphs)-1].edges(data=True))
snap_graph.add_snapshot(graphs[0].edges(data=True), num_in_seq=100)

# subgraph
#sub1 = snap_graph.subgraph(nbunch=[1, 2])
sub2 = snap_graph.subgraph(nbunch=[1, 2], sbunch=[3, 4])

# degree
print("deg: {}".format(snap_graph.degree(nbunch=[2, 3, 4])))
print("deg: {}".format(snap_graph.degree(nbunch=[2, 3, 4], sbunch=[1, 2, 3, 4])))

# number of nodes
print("num nodes: {}".format(snap_graph.number_of_nodes(sbunch=[2, 3, 4])))

# order
print("order: {}".format(snap_graph.order(sbunch=[2, 3, 4])))

# has node
print("has node: {}".format(snap_graph.has_node(n=1, sbunch=[2, 3, 4])))

# is multigraph
print("multigraph: {}".format(snap_graph.is_multigraph(sbunch=[2, 3, 4])))

# is directed
print("is directed: {}".format(snap_graph.is_directed(sbunch=[2, 3, 4])))

# to directed
print("to directed: {}".format(snap_graph.to_directed(sbunch=[2, 3, 4])))

# to undirected
print("to undirected: {}".format(snap_graph.to_undirected(sbunch=[2, 3, 4])))

# size
print("size: {}".format(snap_graph.size(sbunch=[2, 3, 4])))

# get
print("get: {}".format(
    nx.adjacency_matrix(snap_graph.get(sbunch=[4])[0])
))


print()