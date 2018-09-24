from nose.tools import assert_equal
from nose.tools import assert_is
from nose.tools import assert_not_equal
from nose.tools import assert_raises
from nose.tools import assert_true
from nose.tools import raises

import networkx
from dynetworkx.classes.dynamicgraph import DynamicGraph

class TestDynamicGraph(object):
    """ Tests dynamic graph class"""
    def setup(self):
        self.graph = networkx.dynamicgraph()
        ed1, ed2, ed3, ed4, ed5, ed6, ed7 = ({}, {}, {}, {}, {}, {}, {})
        self.k7adj = {0: {1: ed1, 2: ed2},
                      1: {0: ed1, 2: ed3},
                      2: {0: ed2, 1: ed3}}
        self.k7edges = [(0, 1), (0, 2), (1, 2)]
        self.k7nodes = [0, 1, 2, 3, 4, 5, 6]
        self.K7 = self.Graph()
        self.K7.adj = self.K7.edge = self.k3adj
        self.K7.node = {}
        self.K7.node[0] = {}
        self.K7.node[1] = {}
        self.K7.node[2] = {}
        assert(False)

    def test_contains(self):
        assert(False)

    def test_add_node(self):
        assert(False)

    def test_add_edge(self):
        assert(False)

    def test_timestamp_filter(self):
        assert(False)

    def test_node_filter(self):
        assert(False)

    def test_coarsen(self):
        assert(False)

    def test_to_snapshots(self):
        assert(False)
