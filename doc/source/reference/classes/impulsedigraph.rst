.. _ImpulseDigraph:

===============
Directed Impulse Graph
===============

Overview
========
.. currentmodule:: dynetworkx
.. autoclass:: ImpulseDiGraph

Methods
=======

Adding and removing nodes and edges
-----------------------------------

.. autosummary::
   :toctree: generated/

   ImpulseDiGraph.__init__
   ImpulseDiGraph.add_node
   ImpulseDiGraph.add_nodes_from
   ImpulseDiGraph.remove_node
   ImpulseDiGraph.add_edge
   ImpulseDiGraph.add_edges_from
   ImpulseDiGraph.remove_edge


Reporting impulse graph, nodes and edges
-----------------------------------------
.. autosummary::
   :toctree: generated/

   ImpulseDiGraph.nodes
   ImpulseDiGraph.has_node
   ImpulseDiGraph.edges
   ImpulseDiGraph.has_edge
   ImpulseDiGraph.__contains__
   ImpulseDiGraph.__str__
   ImpulseDiGraph.interval


Counting nodes and edges
------------------------
.. autosummary::
   :toctree: generated/

   ImpulseDiGraph.number_of_nodes
   ImpulseDiGraph.__len__


Making copies and subgraphs
---------------------------
.. autosummary::
   :toctree: generated/

   ImpulseDiGraph.to_subgraph
   ImpulseDiGraph.to_snapshots
   ImpulseDiGraph.to_snapshot_graph


Loading an impulse graph
-------------------------
.. autosummary::
   :toctree: generated/

   ImpulseDiGraph.load_from_txt
   ImpulseDiGraph.save_to_txt

Analyzing impulse graphs
-------------------------
.. autosummary::
   :toctree: generated/

   ImpulseDiGraph.degree
   ImpulseDiGraph.in_degree
   ImpulseDiGraph.out_degree