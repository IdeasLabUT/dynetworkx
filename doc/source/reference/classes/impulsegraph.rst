.. _Impulsegraph:

===============
Impulse Graph
===============

Overview
========
.. currentmodule:: dynetworkx
.. autoclass:: ImpulseGraph

Methods
=======

Adding and removing nodes and edges
-----------------------------------

.. autosummary::
   :toctree: generated/

   ImpulseGraph.__init__
   ImpulseGraph.add_node
   ImpulseGraph.add_nodes_from
   ImpulseGraph.remove_node
   ImpulseGraph.add_edge
   ImpulseGraph.add_edges_from
   ImpulseGraph.remove_edge


Reporting impulse graph, nodes and edges
-----------------------------------------
.. autosummary::
   :toctree: generated/

   ImpulseGraph.nodes
   ImpulseGraph.has_node
   ImpulseGraph.edges
   ImpulseGraph.has_edge
   ImpulseGraph.__contains__
   ImpulseGraph.__str__
   ImpulseGraph.interval


Counting nodes and edges
------------------------
.. autosummary::
   :toctree: generated/

   ImpulseGraph.number_of_nodes
   ImpulseGraph.__len__


Making copies and subgraphs
---------------------------
.. autosummary::
   :toctree: generated/

   ImpulseGraph.to_subgraph
   ImpulseGraph.to_snapshots
   ImpulseGraph.to_snapshot_graph


Loading an impulse graph
-------------------------
.. autosummary::
   :toctree: generated/

   ImpulseGraph.load_from_txt
   ImpulseGraph.save_to_txt
   
Analyzing impulse graphs
-------------------------
.. autosummary::
   :toctree: generated/
   
   ImpulseGraph.degree