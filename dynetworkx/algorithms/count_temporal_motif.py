from networkx import Graph
import random
import itertools
import dynetworkx as dnx


def __enumerate_subgraphs(g, size_k):
    """Enumerate all size_k connected subgraph of static graph g.

    Parameters
    ----------
    g: static graph to take sub-graphs from

    size_k: size of sub-graphs

    Returns
    -------
    an iterator for all size_k sub-graphs of g
    """
    for v in g.nodes():
        v_extension = set(filter(lambda x: x > v, g.neighbors(v)))
        yield from __extend_subgraph({v}, v_extension, v, g, size_k)


def __extend_subgraph(v_subgraph, v_extension, v, g, size_k):
    """A recursive helper function for __enumerate_subgraphs() to enumerate all size_k connected sub-graphs

    Parameters
    ----------
    v_subgraph: current set of nodes belong to a sub-graph

    v_extension: current set of possible nodes to extend v_subgraph

    v: starting node of the subgraph

    g: static graph to take sub-graphs from

    size_k: size of sub-graphs

    Returns
    -------
    an iterator for all size_k sub-graphs of g with v as the starting node
    """
    if len(v_subgraph) == size_k:
        yield g.subgraph(v_subgraph)
    else:
        while len(v_extension) != 0:
            w = random.choice(tuple(v_extension))
            v_extension.remove(w)

            v2_extension = v_extension.copy().union(set(filter(lambda x: x > v,
                                                               set(g.neighbors(w)) - v_subgraph)))
            yield from __extend_subgraph(v_subgraph.copy().union({w}), v2_extension, v, g, size_k)


def count_temporal_motif(G, sequence, delta, get_count_dict=False):
    """Count all temporal motifs.

    Parameters
    ----------
    G : the graph to count temporal motif from. This function only supports ImpulseDiGraph

    sequence: a sequence of edges specifying the order of the motif. For example ((1,2), (2,3), (2,1)) means
        1 -> 2 then 2 -> 3 then 2 -> 1. Note: The motif has to be connected.

    delta: time window that specifies the maximum time limit that all edges in a motif must occur within.

    get_count_dict: if True, return the motif count dictionary, which provides greater detail about which
        motifs appear in a certain type of motif. If False, only returns the total count of all motifs of that type.

    Returns
    -------
    count dictionary or total motif count

    Examples
    --------
    >>> G = dnx.ImpulseDiGraph()
    >>> G.add_edge(1, 2, 30)
    >>> G.add_edge(3, 2, 30)
    >>> G.add_edge(4, 2, 30)
    >>> G.add_edge(2, 5, 32)
    >>> G.add_edge(2, 5, 33)
    >>> dnx.count_temporal_motif(G, ((1, 2), (2, 3), (2, 3)), 3)
    3
    >>> dnx.count_temporal_motif(G, ((1, 2), (2, 3), (2, 3)), 3, get_count_dict=True)
    {(1, 2, 2, 5, 2, 5): 1, (4, 2, 2, 5, 2, 5): 1, (3, 2, 2, 5, 2, 5): 1}
    """
    if not isinstance(G, dnx.ImpulseDiGraph):
        raise TypeError('This function only supports ImpulseDiGraph')

    total_counts = dict()
    # this is used later for checking matching sequences
    node_sequence = tuple(node for edge in sequence for node in edge)
    g = Graph(G.to_networkx_graph())
    static_motif = Graph()
    static_motif.add_edges_from(sequence)

    for sub in __enumerate_subgraphs(g, size_k=len(static_motif.nodes())):
        # A way to check if nodes in sub may contain motif will help speed up. Using nx.is_isomorphic() will
        # create error by dropping a lot of potential subgraphs.
        counts = dict()
        edges = list()
        for u, v in itertools.combinations(sub.nodes(), 2):
            edges.extend(G.edges(u, v))
            edges.extend(G.edges(v, u))

        # Motifs with self-loops won't be duplicated when iterating through subgraphs
        for u in sub.nodes():
            edges.extend(G.edges(u, u))

        edges = sorted(edges, key=lambda x: x[2])
        # Count all possible sequences from edges of the static subgraph
        start = 0
        end = 0
        while end < len(edges):
            while edges[start][2] + delta < edges[end][2]:

                # combine all edges having the same timestamps to decrement counts
                tmp_time = edges[start][2]
                same_time_edges = list()

                while edges[start][2] == tmp_time:
                    same_time_edges.append(edges[start][0:2])
                    start += 1
                    if start >= len(edges):
                        break
                __decrement_counts(same_time_edges, len(sequence), counts)

            # combine all edges having the same timestamps to increment counts
            tmp_time = edges[end][2]
            same_time_edges = list()
            while edges[end][2] == tmp_time:
                same_time_edges.append(edges[end][0:2])
                end += 1
                if end >= len(edges):
                    break

            __increment_counts(same_time_edges, len(sequence), counts)

        # Extract out count for sequences that are isomorphic to the temporal motifs
        for keys in sorted(counts.keys()):
            if len(keys) / 2 == len(sequence):
                if counts[keys] == 0:
                    continue

                node_map = dict()
                isomorphic = True
                # check matching sequences (node sequence vs key)
                for n in range(len(node_sequence)):
                    if node_map.get(node_sequence[n]):
                        if node_map[node_sequence[n]] == keys[n]:
                            continue
                        else:
                            isomorphic = False
                            break
                    else:
                        if not keys[n] in node_map.values():
                            node_map[node_sequence[n]] = keys[n]
                        else:
                            isomorphic = False
                            break
                if isomorphic:
                    total_counts[keys] = counts[keys]

    if get_count_dict:
        return total_counts
    else:
        return sum(total_counts.values())


def __decrement_counts(edges, motif_length, counts):
    """Decrement motif counts when removing edges.
    Any potential orders of edges appearing at the same timestamp are ignored
    (for example: when timestamp resolution is too high and edges that may happen one after another are combined
    into 1 timestamp)

    Parameters
    ----------
    edges: list of edges having the same timestamp

    motif_length: length of motif

    counts: a dictionary containing counts of all motifs

    Returns
    -------
    None
    """
    suffixes = sorted(counts.keys(), key=len)
    for e in edges:
        counts[e] -= 1

    for suffix in suffixes:
        if len(suffix) / 2 < motif_length - 1:
            for e in edges:
                if counts.get(e + suffix):
                    counts[e + suffix] -= counts[suffix]


def __increment_counts(edges, motif_length, counts):
    """Increment motif counts when adding edges.
    Any potential orders of edges appearing at the same timestamp are ignored
    (for example: when timestamp resolution is too high and edges that may happen one after another are combined
    into 1 timestamp)

    Parameters
    ----------
    edges: list of edges having the same timestamp

    motif_length: length of motif

    counts: a dictionary containing counts of all motifs

    Returns
    -------
    None
    """
    prefixes = sorted(counts.keys(), key=len, reverse=True)
    for prefix in prefixes:
        if len(prefix) / 2 < motif_length:
            for e in edges:
                if counts.get(prefix + e) is None:
                    counts[prefix + e] = 0
                counts[prefix + e] += counts[prefix]

    for e in edges:
        if counts.get(e) is None:
            counts[e] = 0
        counts[e] += 1
