..  -*- coding: utf-8 -*-

Tutorial
========

.. currentmodule:: dynetworkx

This guide can help you start working with IntervalGraph module of DyNetworkX.

Creating an interval graph
--------------------------

Create an empty interval graph with no nodes and no edges.

    >>> import dynetworkx as dnx
    >>> G = dnx.IntervalGraph()

By definition, an :class:`IntervalGraph` is a collection of nodes (vertices) along with
identified pairs of nodes (called interval edges, edges, links, etc) each of which is
coupled with a given interval. In DyNetworkX, just like NetworkX, nodes can be any
hashable object e.g., a text string, an image, an XML object, another Graph,
a customized node object, etc.

.. note:: Python's ``None`` object should not be used as a node as it determines
   whether optional function arguments have been assigned in many functions.
