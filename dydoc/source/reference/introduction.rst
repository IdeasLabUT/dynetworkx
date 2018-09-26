.. _introduction:

Introduction
============

.. currentmodule:: dynetworkx

The structure of DyNetworkX closely (and intentionally) resembles the structure of NetworkX, since
it is a fork of NetworkX.

DyNetworkX Basics
-----------------

After starting Python, import the dynetworkx module with (the recommended way)

   >>> import dynetworkx as dnx

To save repetition, in the documentation we assume that DyNetworkX has been imported this way.

If importing networkx fails, it means that Python cannot find the installed
module. Check your installation and your ``PYTHONPATH``.

The following basic graph types are provided as Python classes:

:class:`IntervalGraph`
   This class implements an undirected interval graph. Each edge
   must have a beginning and ending as an interval. It ignores
   multiple edges (edges with the same nodes and interval)
   between two nodes.  It does allow self-loop edges between
   a node and itself.

:class:`SnapshotGraph`
   This class implements an easy way to divide any type of Networkx graph
   to separate snapshots. This class is still in its early stages of development.

:class:`DynamicGraph`
    This class implements a continuous dynamic graph with edges, name, and graph attributes.
