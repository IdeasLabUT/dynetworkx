.. _Intervalgraph:

===============
Interval Graph
===============

Overview
========
.. currentmodule:: dynetworkx
.. autoclass:: IntervalGraph

Methods
=======

Adding and removing nodes and edges
-----------------------------------

.. autosummary::
   :toctree: generated/

   IntervalGraph.__init__
   IntervalGraph.add_node
   IntervalGraph.add_nodes_from
   IntervalGraph.remove_node
   IntervalGraph.add_edge
   IntervalGraph.add_edges_from
   IntervalGraph.remove_edge


Reporting interval graph, nodes and edges
-----------------------------------------
.. autosummary::
   :toctree: generated/

   IntervalGraph.nodes
   IntervalGraph.has_node
   IntervalGraph.edges
   IntervalGraph.has_edge
   IntervalGraph.__contains__
   IntervalGraph.__str__
   IntervalGraph.interval


Counting nodes and edges
------------------------
.. autosummary::
   :toctree: generated/

   IntervalGraph.number_of_nodes
   IntervalGraph.__len__


Making copies and subgraphs
---------------------------
.. autosummary::
   :toctree: generated/

   IntervalGraph.to_subgraph
   IntervalGraph.to_snapshots


Loading an interval graph
-------------------------
.. autosummary::
   :toctree: generated/

   IntervalGraph.load_from_txt
