.. _SnapshotDigraph:

===============
Directed Snapshot Graph
===============

Overview
========
.. currentmodule:: dynetworkx
.. autoclass:: SnapshotDiGraph

Methods
=======

Adding and removing nodes and edges
-----------------------------------

.. autosummary::
   :toctree: generated/

   SnapshotDiGraph.__init__
   SnapshotDiGraph.add_nodes_from
   SnapshotDiGraph.add_edges_from


Manipulating Snapshots
----------------------
.. autosummary::
   :toctree: generated/

   SnapshotDiGraph.insert
   SnapshotDiGraph.add_snapshot

Reporting Snapshots
-------------------
.. autosummary::
   :toctree: generated/

   SnapshotDiGraph.__len__
   SnapshotDiGraph.order
   SnapshotDiGraph.has_node
   SnapshotDiGraph.size
   SnapshotDiGraph.is_directed
   SnapshotDiGraph.is_multigraph
   SnapshotDiGraph.number_of_nodes
   SnapshotDiGraph.degree



Making copies and subgraphs
---------------------------
.. autosummary::
   :toctree: generated/

   SnapshotDiGraph.subgraph
   SnapshotDiGraph.to_directed
   SnapshotDiGraph.to_undirected

