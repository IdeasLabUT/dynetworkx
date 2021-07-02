import dynetworkx as dnx


def test_count_temporal_motif():
    G = dnx.ImpulseDiGraph()
    G.add_edge(1, 2, 3)
    G.add_edge(2, 1, 8)
    G.add_edge(2, 3, 8)
    G.add_edge(3, 4, 8)
    G.add_edge(2, 1, 14)
    G.add_edge(4, 5, 15)
    G.add_edge(2, 1, 18)
    G.add_edge(2, 3, 18)
    G.add_edge(2, 3, 20)
    G.add_edge(2, 1, 22)
    G.add_edge(2, 3, 25)

    assert dnx.count_temporal_motif(G, ((1, 2), (1, 3), (1, 2)), 5) == 2
    assert dnx.count_temporal_motif(G, ((1, 2), (1, 3), (1, 2)), 5, get_count_dict=True) == \
           {(2, 1, 2, 3, 2, 1): 1, (2, 3, 2, 1, 2, 3): 1}

    # test simultaneous timestamps
    G.add_edge(1, 2, 30)
    G.add_edge(3, 2, 30)
    G.add_edge(4, 2, 30)
    G.add_edge(2, 5, 32)
    G.add_edge(2, 5, 33)
    assert dnx.count_temporal_motif(G, ((1, 2), (2, 3), (2, 3)), 3) == 3
    assert dnx.count_temporal_motif(G, ((1, 2), (2, 3), (2, 3)), 3, get_count_dict=True) == \
           {(1, 2, 2, 5, 2, 5): 1, (4, 2, 2, 5, 2, 5): 1, (3, 2, 2, 5, 2, 5): 1}
    assert dnx.count_temporal_motif(G, ((1, 2), (3, 2), (4, 2)), 3) == 0

    try:
        G1 = dnx.IntervalGraph()
        dnx.count_temporal_motif(G1, ((1, 2), (1, 3), (1, 2)), 5)
    except TypeError:
        assert 1
    else:
        assert 0
