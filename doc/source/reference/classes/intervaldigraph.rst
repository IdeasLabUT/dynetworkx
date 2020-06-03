.. _IntervalDigraph:

===============
Directed Interval Graph
===============

Overview
========
.. currentmodule:: dynetworkx
.. autoclass:: IntervalDiGraph

Methods
=======

Adding and removing nodes and edges
-----------------------------------

.. autosummary::
   :toctree: generated/

   IntervalDiGraph.__init__
   IntervalDiGraph.add_node
   IntervalDiGraph.add_nodes_from
   IntervalDiGraph.remove_node
   IntervalDiGraph.add_edge
   IntervalDiGraph.add_edges_from
   IntervalDiGraph.remove_edge


Reporting interval graph, nodes and edges
-----------------------------------------
.. autosummary::
   :toctree: generated/

   IntervalDiGraph.nodes
   IntervalDiGraph.has_node
   IntervalDiGraph.edges
   IntervalDiGraph.has_edge
   IntervalDiGraph.__contains__
   IntervalDiGraph.__str__
   IntervalDiGraph.interval


Counting nodes and edges
------------------------
.. autosummary::
   :toctree: generated/

   IntervalDiGraph.number_of_nodes
   IntervalDiGraph.__len__


Making copies and subgraphs
---------------------------
.. autosummary::
   :toctree: generated/

   IntervalDiGraph.to_subgraph
   IntervalDiGraph.to_snapshots


Loading an interval graph
-------------------------
.. autosummary::
   :toctree: generated/

   IntervalDiGraph.load_from_txt
   IntervalDiGraph.save_to_txt
   IntervalDiGraph.from_networkx_graph
   IntervalDiGraph.from_snapshots

Analyzing interval graphs
-------------------------
.. autosummary::
   :toctree: generated/

   IntervalDiGraph.degree
   IntervalDiGraph.in_degree
   IntervalDiGraph.out_degree