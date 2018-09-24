import networkx as nx
import dynetworkx as dx

# def wrapper(method):

def k_core(snapshot_graph, k=None, core_number=None):
    result = []
    for snapshot in snapshot_graph.snapshots:
        result.append(nx.algorithms.core.k_core(snapshot, k, core_number))
    return result
