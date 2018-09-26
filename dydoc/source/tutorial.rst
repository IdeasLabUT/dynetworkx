..  -*- coding: utf-8 -*-

Tutorial
========

.. currentmodule:: dynetworkx

This guide can help you start working with IntervalGraph module of DyNetworkX.

**Disclaimer:**
this tutorial, similar to DyNetworkX itself, is heavily influenced by NetworkX's tutorial.
This is done on purpose, in order to point out the similarities between the two packages.

Creating an interval graph
--------------------------

Create an empty interval graph with no nodes and no edges.

    >>> import dynetworkx as dnx
    >>> IG = dnx.IntervalGraph()

By definition, an :class:`IntervalGraph` is a collection of nodes (vertices) along with
identified pairs of nodes (called interval edges, edges, links, etc) each of which is
coupled with a given interval. In DyNetworkX, just like NetworkX, nodes can be any
hashable object e.g., a text string, an image, an XML object, another Graph,
a customized node object, etc.

.. note:: Python's ``None`` object should not be used as a node as it determines
   whether optional function arguments have been assigned in many functions.

Nodes
-----

Using DyNetworkX's :class:`IntervalGraph.load_from_txt` method, the graph
``IG`` can be grown by importing an existing network. However, we first
look at simple ways to manipulate an interval graph. The simplest
form is adding a single node,

    >>> IG.add_node(1)

add alist of nodes,

    >>> IG.add_nodes_from([2, 3])

or add any iterable container of nodes. You can also add nodes along with node
attributes if your container yields 2-tuples (node, node_attribute_dict).
Node attributes are discussed further below.

    >>> H = dnx.IntervalGraph()
    >>> IG.add_node(H)

Note that interval graph ``IG`` now contains interval graph ``H`` as a node.
This flexibility is very powerful as it allows graphs of graphs, graphs
of files, graphs of functions and much more. It is worth thinking
about how to structure your application so that the nodes are
useful entities.  Of course you can always use a unique
identifier in ``IG``and have a separate dictionary
keyed by identifier to the node information if
you prefer.

.. note:: You should not change the node object if the hash depends
   on its contents.

Edges
-----

Edges are what make an interval graph possible. Every edge is defined by 2 nodes, the
inclusive beginning of the interval when the edge first appears and its
non-inclusive end. beginning of an interval must be strictly smaller
than its end and both can be of any orderable types.

.. note:: In this tutotial as well as IntervalGraph documentation, the two terms ``edge``
   and ``interval edge`` are used interchangeably.

``IG`` can also be grown by adding one edge at a time,

   >>> IG.add_edge(1, 2, 1, 4)
   >>> ie = (2, 3, 2, 5)
   >>> IG.add_edge(*ie) # unpack interval edge tuple*

by adding a list of edges,

    >>> IG.add_edges_from([(1, 2, 2, 6), (1, 3, 6, 9)])

or by adding any :term:`ebunch` of edges. An *ebunch* is any iterable container of
interval edge-tuples. An interval edge-tuple is a 4-tuple of nodes and intervals.

.. note:: In above example it is worth noting that the two added interval edges,
   ``(1, 2, 1, 4)`` and ``(1, 2, 2, 6)`` are two different interval edges,
   since they exists on different interval.

If a new interval edge is to be added with nodes that are not currently in the
interval graph, nodes will be added automatically.

There are no complaints when adding existing nodes or edges. As we add new
nodes/edges, DyNetworkX quietly ignores any that are already present.

   >>> IG.add_edge(1, 2, 1, 4)
   >>> IG.add_node(1)

At this stage the interval graph ``IG`` consist of 4 nodes and 4 edges,

   >>> IG.number_of_nodes()
   4
   >>> len(IG.edges())
   4

We can examine the nodes and edges. Two basic grpah properties facilitate reporting:
:class:`IntervalGraph.nodes()` and :class:`IntervalGraph.edges()`. These are lists
of the nodes and interval edges. They offer a continually updated read-only view
into the graph structure.

   >>> IG.nodes()
   [1, 2, 3, <dynetworkx.classes.intervalgraph.IntervalGraph object at 0x100000000>]

``IG.edges()`` is an extremely flexible and useful method to query the interval
graph for various interval edges. It returns a list of Interval objects which
are in the form ``Interval(begin, end, (node_1, node_2)``.

Using this method you have access to 4 constraints in order to restrict your query.
`u`, `v`, `begin` and `end`. Defining any of them narrows down your query.

   >>> IG.edges() # returns a list of all edges
   [Interval(6, 9, (1, 3)), Interval(2, 5, (2, 3)), Interval(2, 6, (1, 2)), Interval(1, 4, (1, 2))]
   >>> IG.edges(begin=5) # all edges which have an overlapping interval with interval [5, end of the interval graph]
   [Interval(6, 9, (1, 3)), Interval(2, 6, (1, 2))]
   >>> IG.edges(end=3) # all edges which have an overlapping interval with interval [beginning of the interval graph, 3)
   [Interval(2, 5, (2, 3)), Interval(2, 6, (1, 2)), Interval(1, 4, (1, 2))]
   >>> IG.edges(u=1, v=2) # all edge between nodes 1 and 2
   [Interval(2, 6, (1, 2)), Interval(1, 4, (1, 2))]
   >>> IG.edges(1, 2, 5, 6) # all edges between nodes 1 and 2 which have an overlapping interval with [5, 6)
   [Interval(2, 6, (1, 2))]

As it is shown, ``IG.edges()`` is a powerful method to query the network for edges.
You can also take advantage of :class:`IntervalGraph.has_node()` and
:class:`IntervalGraph.has_edge()` as it is shown below,

   >>> IG.has_node(3)
   True
   >>> 1 in IG # this is equivalent to IG.has_node(1)
   True
   >>> IG.has_node(5)
   False
   >>> IG.has_edge(2, 3)
   True
   >>> IG.has_edge(1, H)
   False

   Or constraint the begin and/or end of your search:

   >>> IG.has_node(3, end=2) # end is non-inclusive
   False

   >>> IG.has_edge(2, 3, 3, 7) # matching an interval edge with nodes 2 and 3, and overlapping interval [3, 7)
   True
   >>> IG.has_edge(2, 3, 3, 7, overlapping=False) # setting overlapping=False, searches for an exact interval match
   False

