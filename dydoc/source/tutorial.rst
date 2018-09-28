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

Using DyNetworkX's :meth:`IntervalGraph.load_from_txt` method, the graph
``IG`` can be grown by importing an existing network. However, we first
look at simple ways to manipulate an interval graph. The simplest
form is adding a single node,

    >>> IG.add_node(1)

add a list of nodes,

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
identifier in ``IG`` and have a separate dictionary
keyed by identifier to the node information if
you prefer.

.. note:: You should not change the node object if the hash depends
   on its contents.

Edges
-----

Edges are what make an interval graph possible. Every edge is defined by 2 nodes, the
inclusive beginning of the interval when the edge first appears and its
non-inclusive end. Beginning of an interval must be strictly smaller
than its end and both can be of any orderable types.

.. note:: In this tutotial as well as IntervalGraph documentation, the two terms ``edge``
   and ``interval edge`` are used interchangeably.

``IG`` can also be grown by adding one edge at a time,

   >>> IG.add_edge(1, 2, 1, 4) # n1, n2, beginning, end of the edge interval
   >>> ie = (2, 3, 2, 5)
   >>> IG.add_edge(*ie) # unpack interval edge tuple*

by adding a list of edges,

    >>> IG.add_edges_from([(1, 2, 2, 6), (1, 3, 6, 9)])

or by adding any `ebunch` of edges. An *ebunch* is any iterable container of
interval edge-tuples. An interval edge-tuple is a 4-tuple of nodes and intervals.

.. note:: In above example it is worth noting that the two added interval edges,
   ``(1, 2, 1, 4)`` and ``(1, 2, 2, 6)`` are two different interval edges,
   since they exists on different intervals.

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

We can examine nodes and edges with two interval graph methods which facilitate reporting:
:meth:`IntervalGraph.nodes()` and :meth:`IntervalGraph.edges()`. These are lists
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

One can also take advantage of this method to obtain more information such as
`degree`. Since in an interval graph these parameters change depending on
the interval in question, you need to adjust your query.

Accessing `degree` of a node:

   >>> len(IG.edges(u=1)) # total number of edges associated with node 1 over the entire interval
   3
   >>> len(IG.edges(u=1, begin=2, end=4)) # Adding interval restriction
   2

Keep in mind that ``end`` is non-inclusive. Thus, depening on what time increment you use
to define your interval, if you set ``end = begin + smallest_increment`` it will
return all the edges which are present at time ``begin``.

   >>> len(IG.edges(u=1, begin=5, end=6))
   1

If you are using a truly continuous time interval, you can add your machine epsilon to
``begin`` to achieve the same result. As an example:

   >>> import numpy as np
   >>> eps = np.finfo(np.float64).eps
   >>> begin = 5
   >>> IG.edges(u=1, begin=begin, end=begin + eps)
   [Interval(2, 6, (1, 2))]


As it is shown, ``IG.edges()`` is a powerful method to query the network for edges.
You can also take advantage of :meth:`IntervalGraph.has_node()` and
:meth:`IntervalGraph.has_edge()` as it is shown below,

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

One can remove nodes and edges from the graph in a similar fashion to adding.
by using :meth:`IntervalGraph.remove_node` and
:meth:`IntervalGraph.remove_edge`, e.g.

   >>> IG.remove_node(H)
   [1, 2, 3]
   >>> IG.remove_edge(1, 3, 6, 9, overlapping=False)
   >>> IG.edges()
   [Interval(2, 5, (2, 3)), Interval(2, 6, (1, 2)), Interval(1, 4, (1, 2))]


What to use as nodes and edges
------------------------------
Just like NetworkX, DyNetworkX does not have a specific type for nodes an edges.
This allows you to represent nodes and edges with any hashable object to add
more depth and meanning to your interval graph. The most common choices are
numbers or strings, but a node can be any hashable object (except ``None``),
and an edge can be associated with any object ``x`` using
``IG.add_edge(n1, n2, begin, end, object=x)``.

As an example, ``n1`` and ``n2`` could be real people's profile url or a
custom python object and ``x`` can be another python object which
describes the detail of their contact. This way, you are not
bound to only associating weights with the edges.

Based on the NetworkX's experience, this is quite useful, but its abuse
can lead to unexpected surprises unless one is familiar with Python.

Adding attributes to graphs, nodes, and edges
---------------------------------------------
Attributes such as weights, labels, colors, or whatever Python object you like,
can be attached to graphs, nodes, or edges.

Each graph, node, and edge can hold key/value attribute pairs in an associated
attribute dictionary (the keys must be hashable).  By default these are empty,
but attributes can be added or changed using ``add_edge``, ``add_node``.

Graph attributes
~~~~~~~~~~~~~~~~

Assign graph attributes when creating a new graph,

    >>> IG = dnx.IntervalGraph(state='Ohio')
    >>> IG.graph
    {'state': 'Ohio'}

Or you can  modify attributes later,

   >>> IG.graph['state'] = 'Michigan'
   >>> IG.graph
   {'state': 'Michigan'}

There is also an spacial attribute for interval graphs called ``name``. You
can either set it just like any other attribute or you can take advantage
of the ``IG.name`` property:

   >>> IG.name = "USA"
   >>> IG.name
   USA

Node attributes
~~~~~~~~~~~~~~~

Add node attributes using ``add_node()`` or ``add_nodes_from()``,

    >>> IG.add_node(1, time='5pm', day="Friday") # Adds node 1 and sets its two attributes
    >>> IG.add_nodes_from([2, 3], time='2pm') # Adds nodes 2 and 3 and sets both of their 'time' attributes to '2pm'
    >>> IG.add_node(1, time='10pm') # Updates node 1's 'time' attribute to '10pm'

Note that you can update a node's attribute by adding the node and setting a new value for its attribute.


Edge attributes
~~~~~~~~~~~~~~~

Similarly, add/change edge attributes using ``add_edge()`` or ``add_edges_from()``,

   >>> G.add_edge(1, 2, 4, 6, contact_type='call') # Adds the edge and sets its 'contact_type' attribute.
   >>> G.add_edges_from([(3, 4, 1, 5), (1, 2, 4, 6)], weight=5.8)
   >>> G.add_edge(1, 2, 4, 6, weight=6.6) # Updates the weight attribute of the edge.

Note that updating an edge's attribute is similar to updating nodes' attributes.

Subgraphs and snapshots
-----------------------

You can create one, or a series of snapshots of, NetworkX `Graph` or `MultiGraph` from
an interval graph if you wish to analyze a portion, or your entire interval graph,
using well-known static network algorithms that are available in NetworkX.

Subgraphs
~~~~~~~~~

To extract a portion of an interval graph, given an interval,
you can utilize :meth:`IntervalGraph.to_subgraph`,

   >>> IG = dnx.IntervalGraph()
   >>> IG.add_edges_from([(1, 2, 3, 10), (2, 4, 1, 11), (6, 4, 12, 19), (2, 4, 8, 15)])
   >>> H = IG.to_subgraph(4, 12)
   >>> type(H)
   <class 'networkx.classes.graph.Graph'>
   >>> list(H.edges(data=True))
   [(1, 2, {}), (2, 4, {})]

Note that you can also use :meth:`IntervalGraph.interval` to get the interval for the
entire interval graph, and use that to convert an interval graph to a NetworkX Graph.

You can also keep the information about each edge's interval as attributes on the
NetworkX's Graph:

   >>> H = G.to_subgraph(4, 12, edge_interval_data=True)
   >>> type(H)
   <class 'networkx.classes.graph.Graph'>
   >>> list(H.edges(data=True))
   [(1, 2, {'end': 10, 'begin': 3}), (2, 4, {'end': 15, 'begin': 8})]

Notice that if there are multiple edges available between two nodes, the interval information
is going to reflect only one of the edges. Another option is to retrieve a `MultiGraph` to
lose less information in the conversion process:

   >>> M = G.to_subgraph(4, 12, multigraph=True, edge_interval_data=True)
   >>> type(M)
   <class 'networkx.classes.multigraph.MultiGraph'>
   >>> list(M.edges(data=True))
   [(1, 2, {'end': 10, 'begin': 3}), (2, 4, {'end': 11, 'begin': 1}), (2, 4, {'end': 15, 'begin': 8})]


Snapshots
~~~~~~~~~

A more traditional method of analyzing continuous dynamic networks has been dividing the
network into a series of fixed-interval snapshots. Although some information will be
lost in the conversion due to the classic limitations of representing a continuous
network in a discrete format, you will gain access to numerous well-defined
algorithms which do not exist for continuous networks.

To do so, you can simply use :meth:`IntervalGraph.to_snapshots` and set the number of
snapshots you wish to divided the network into:

    >>> S, l = G.to_snapshots(2, edge_interval_data=True, return_length=True)
    >>> S # a list of NetworkX Graphs
    [<networkx.classes.graph.Graph object at 0x100000>, <networkx.classes.graph.Graph object at 0x150d00>]
    >>> l # length of the interval of a single snapshot
    9.0
    >>> for g in S:
    >>> ... g.edges(data=True))
    [(1, 2, {'begin': 3, 'end': 10}), (2, 4, {'begin': 8, 'end': 15})]
    [(2, 4, {'begin': 8, 'end': 15}), (4, 6, {'begin': 12, 'end': 19})]


Combining this method with :class:`SnapshotGraph` can be a powerful tool to gain access
to all the methods available through DyNetworkX's :class:`SnapshotGraph`.

Similar to `to_subgraph` method, you can also divide the interval graph into a series of
NetworkX's `MultiGraph`, if that is what you need.

Importing from text file
------------------------

Using `load_from_txt` you can also read in an interval graph from a text file in an
specific edge-list format. For more detail checkout the documentation on
:meth:`IntervalGraph.load_from_txt`.

