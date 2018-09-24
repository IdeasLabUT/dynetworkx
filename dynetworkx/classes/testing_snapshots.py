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

snap_graph = SnapshotGraph()
for g in graphs:
    snap_graph.add_snapshot(g.edges(data=True))

snap_graph.add_snapshot(graphs[len(graphs)-1].edges(data=True))
snap_graph.add_snapshot(graphs[0].edges(data=True), num_in_seq=100)
snap_graph.insert(graphs[1], snap_len=1, num_in_seq=40)

print(len(snap_graph))

print()