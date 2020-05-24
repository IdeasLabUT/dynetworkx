.. _Snapshotgraph:

===============
Snapshot Graph
===============

Overview
========
.. currentmodule:: dynetworkx
.. autoclass:: SnapshotGraph

Methods
=======

Adding and removing nodes and edges
-----------------------------------

.. autosummary::
   :toctree: generated/

   SnapshotGraph.__init__
   SnapshotGraph.add_nodes_from
   SnapshotGraph.add_edges_from


Manipulating Snapshots
----------------------
.. autosummary::
   :toctree: generated/

   SnapshotGraph.insert
   SnapshotGraph.add_snapshot

Reporting Snapshots
-------------------
.. autosummary::
   :toctree: generated/

   SnapshotGraph.__len__
   SnapshotGraph.order
   SnapshotGraph.has_node
   SnapshotGraph.size
   SnapshotGraph.is_directed
   SnapshotGraph.is_multigraph
   SnapshotGraph.number_of_nodes
   SnapshotGraph.degree



Making copies and subgraphs
---------------------------
.. autosummary::
   :toctree: generated/

   SnapshotGraph.subgraph
   SnapshotGraph.to_directed
   SnapshotGraph.to_undirected

