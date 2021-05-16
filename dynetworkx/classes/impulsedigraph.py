from dynetworkx.classes.impulsegraph import ImpulseGraph
from networkx.classes.digraph import DiGraph
from networkx.exception import NetworkXError
from sortedcontainers import SortedDict, SortedList
from networkx.classes.multidigraph import MultiDiGraph
from networkx.classes.reportviews import NodeView, EdgeView, NodeDataView
import random
import itertools
from networkx import Graph
import networkx as nx
import re


class ImpulseDiGraph(ImpulseGraph):
    """Base class for directed impulse graphs.

    The ImpulseDiGraph class allows any hashable object as a node
    and can associate key/value attribute pairs with each directed edge.

    Each edge must have one integer, timestamp.

    Self-loops are allowed.
    Multiple edges between two nodes are allowed.

    Parameters
    ----------
    attr : keyword arguments, optional (default= no attributes)
        Attributes to add to graph as key=value pairs.

    Examples
    --------
    Create an empty graph structure (a "null impulse graph") with no nodes and
    no edges.

    >>> G = dnx.ImpulseDiGraph()

    G can be grown in several ways.

    **Nodes:**

    Add one node at a time:

    >>> G.add_node(1)

    Add the nodes from any container (a list, dict, set or
    even the lines from a file or the nodes from another graph).

    Add the nodes from any container (a list, dict, set)

    >>> G.add_nodes_from([2, 3])
    >>> G.add_nodes_from(range(100, 110))

    **Edges:**

    G can also be grown by adding edges. This can be considered
    the primary way to grow G, since nodes with no edge will not
    appear in G in most cases. See ``G.to_snapshot()``.

    Add one edge, with timestamp of 10.

    >>> G.add_edge(1, 2, 10)

    a list of edges,

    >>> G.add_edges_from([(1, 2, 10), (1, 3, 11)])

    If some edges connect nodes not yet in the graph, the nodes
    are added automatically. There are no errors when adding
    nodes or edges that already exist.

    **Attributes:**

    Each impulse graph, node, and edge can hold key/value attribute pairs
    in an associated attribute dictionary (the keys must be hashable).
    By default these are empty, but can be added or changed using
    add_edge, add_node.

    Keep in mind that the edge timestamp is not an attribute of the edge.

    >>> G = dnx.ImpulseDiGraph(day="Friday")
    >>> G.graph
    {'day': 'Friday'}

    Add node attributes using add_node(), add_nodes_from()

    >>> G.add_node(1, time='5pm')
    >>> G.add_nodes_from([3], time='2pm')

    Add edge attributes using add_edge(), add_edges_from().

    >>> G.add_edge(1, 2, 10, weight=4.7 )
    >>> G.add_edges_from([(3, 4, 11), (4, 5, 33)], color='red')

    **Shortcuts:**

    Here are a couple examples of available shortcuts:

    >>> 1 in G  # check if node in impulse graph during any timestamp
    True
    >>> len(G)  # number of nodes in the entire impulse graph
    5

    **Subclasses (Advanced):**
    Edges in impulse graphs are represented by tuples kept in a SortedDict
    (http://www.grantjenks.com/docs/sortedcontainers/) keyed by timestamp.

    The Graph class uses a dict-of-dict-of-dict data structure.
    The outer dict (node_dict) holds adjacency information keyed by nodes.
    The next dict (adjlist_dict) represents the adjacency information and holds
    edge data keyed by interval objects. The inner dict (edge_attr_dict) represents
    the edge data and holds edge attribute values keyed by attribute names.
    """

    def __init__(self, **attr):
        """Initialize an impulse graph with edges, name, or graph attributes.

        Parameters
        ----------
        attr : keyword arguments, optional (default= no attributes)
            Attributes to add to graph as key=value pairs.

        Examples
        --------
        >>> G = dnx.ImpulseDiGraph()
        >>> G = dnx.ImpulseDiGraph(name='my graph')
        >>> G.graph
        {'name': 'my graph'}
        """

        self.tree = SortedDict()
        self.graph = {}  # dictionary for graph attributes
        self._node = {}
        self._pred = {}  # out
        self._succ = {}  # in
        self.edgeid = 0

        self.graph.update(attr)

    def add_edge(self, u, v, t, **attr):
        """Add an edge between u and v, at t.

        The nodes u and v will be automatically added if they are
        not already in the impulse graph.

        Edge attributes can be specified with keywords or by directly
        accessing the edge's attribute dictionary. See examples below.

        Parameters
        ----------
        u, v : nodes
            Nodes can be, for example, strings or numbers.
            Nodes must be hashable (and not None) Python objects.
        t : timestamp
            Timestamps can be, for example, strings or numbers.
            Timestamps must be hashable (and not None) Python objects.
        attr : keyword arguments, optional
            Edge data (or labels or objects) can be assigned using
            keyword arguments.

        See Also
        --------
        add_edges_from : add a collection of edges

        Notes
        -----
        Adding an edge that already exists updates the edge data.

        Timestamps must be the same type across all edges in the impulse graph.
        Also, to create snapshots, timestamps must be integers.

        Many NetworkX algorithms designed for weighted graphs use
        an edge attribute (by default `weight`) to hold a numerical value.

        Examples
        --------
        The following all add the edge e=(1, 2, 3, 10) to graph G:

        >>> G = dnx.ImpulseDiGraph()
        >>> e = (1, 2, 10)
        >>> G.add_edge(1, 2, 10)           # explicit two-node form with timestamp
        >>> G.add_edge(*e)             # single edge as tuple of two nodes and timestamp
        >>> G.add_edges_from([(1, 2, 10)])  # add edges from iterable container

        Associate data to edges using keywords:

        >>> G.add_edge(1, 2, 10 weight=3)
        >>> G.add_edge(1, 3, 9, weight=7, capacity=15, length=342.7)
        """

        self.tree.setdefault(t, set()).add((u, v))

        self._node.setdefault(u, {})
        self._node.setdefault(v, {})
        self._pred.setdefault(u, {}).setdefault(v, {})[(u, v, t)] = attr
        self._succ.setdefault(v, {}).setdefault(u, {})[(u, v, t)] = attr

    def add_edges_from(self, ebunch_to_add, **attr):
        """Add all the edges in ebunch_to_add.

        Parameters
        ----------
        ebunch_to_add : container of edges
            Each edge given in the container will be added to the
            impulse graph. The edges must be given as as 3-tuples (u, v, t).
            Timestamp must be orderable and the same type across all edges.
        attr : keyword arguments, optional
            Edge data (or labels or objects) can be assigned using
            keyword arguments.

        See Also
        --------
        add_edge : add a single edge

        Notes
        -----
        Adding the same edge (with the same timestamp) twice has no effect
        but any edge data will be updated when each duplicate edge is added.

        Examples
        --------
        >>> G = dnx.ImpulseDiGraph()
        >>> G.add_edges_from([(1, 2, 10), (2, 4, 11)]) # using a list of edge tuples

        Associate data to edges

        >>> G.add_edges_from([(1, 2, 10), (2, 4, 11)], weight=3)
        >>> G.add_edges_from([(3, 4, 19), (1, 4, 3)], label='WN2898')
        """

        for e in ebunch_to_add:
            if len(e) != 3:
                raise NetworkXError("Edge tuple {0} must be a 3-tuple.".format(e))
            self.add_edge(e[0], e[1], e[2], **attr)

    def has_edge(self, u, v, begin=None, end=None, inclusive=(True, True)):
        """Return True if there exists an edge between u and v
        in the impulse graph, during the given interval.

        Parameters
        ----------
        u, v : nodes
            Nodes can be, for example, strings or numbers.
            Nodes must be hashable (and not None) Python objects.
        begin : int or float, optional (default= beginning of the entire impulse graph)
        end : int or float, optional (default= end of the entire impulse graph)
            Must be bigger than or equal begin.
        inclusive: 2-tuple boolean that determines inclusivity of begin and end

        Examples
        --------
        >>> G = dnx.ImpulseDiGraph()
        >>> G.add_edges_from([(1, 2, 10), (2, 4, 11)])
        >>> G.has_edge(1, 2)
        True
        >>> G.has_edge(1, 2, begin=2)
        True
        >>> G.has_edge(2, 4, begin=12)
        False
        """

        if u not in self._pred or v not in self._pred[u]:
            return False

        if begin is None and end is None:
            return True

        if begin and end and begin > end:
            raise NetworkXError("IntervalGraph: interval end must be bigger than or equal to begin: "
                                "begin: {}, end: {}.".format(begin, end))

        for iv in self._pred[u][v]:
            if self.__in_interval(iv[2], begin, end, inclusive=inclusive):
                return True
        return False

    def edges(self, u=None, v=None, begin=None, end=None, inclusive=(True, True), data=False, default=None):
        """Returns a list of tuples of the ImpulseDiGraph edges.

        All edges which are present within the given interval.

        All parameters are optional. `u` and `v` can be thought of as constraints.
        If no node is defined, all edges within the interval are returned.
        If one node is defined, all edges which have that node as one end,
        will be returned, and finally if both nodes are defined then all
        edges between the two nodes are returned.

        Parameters
        ----------
        u, v : nodes, optional (default=None)
            Nodes can be, for example, strings or numbers.
            Nodes must be hashable (and not None) Python objects.
            If the node does not exist in the graph, a key error is raised.
        begin: int or float, optional  (default= beginning of the entire impulse graph)
        end: int or float, optional  (default= end of the entire impulse graph)
            Must be bigger than or equal to begin.
        inclusive: 2-tuple boolean that determines inclusivity of begin and end
        data : string or bool, optional (default=False)
            If True, return 2-tuple (Edge Tuple, dict of attributes).
            If False, return just the Edge Tuples.
            If string (name of the attribute), return 2-tuple (Edge Tuple, attribute value).
        default : value, optional (default=None)
            Default Value to be used for edges that don't have the requested attribute.
            Only relevant if `data` is a string (name of an attribute).

        Returns
        -------
        List of Edge Tuples
            An edge tuple has the following format: (u, v, edge_id, timestamp)

            When called, if `data` is False, a list of edge tuples.
            If `data` is True, a list of 2-tuples: (Edge Tuple, dict of attribute(s) with values),
            If `data` is a string, a list of 2-tuples (Edge Tuple, attribute value).

        Examples
        --------
        To get a list of all edges:

        >>> G = dnx.ImpulseDiGraph()
        >>> G.add_edges_from([(1, 2, 10), (2, 4, 11), (6, 4, 19), (2, 4, 15)])
        >>> G.edges()
        [(1, 2, 10), (2, 4, 11), (2, 4, 15), (6, 4, 19)]

        To get edges which appear in a specific interval:

        >>> G.edges(begin=10)
        [(1, 2, 10), (2, 4, 11), (2, 4, 15), (6, 4, 19)]
        >>> G.edges(end=11)
        [(1, 2, 10), (2, 4, 11)]
        >>> G.edges(begin=11, end=15)
        [(2, 4, 11), (2, 4, 15)]

        To get edges with either of the two nodes being defined:

        >>> G.edges(u=2)
        [(2, 4, 11), (2, 4, 15)]
        >>> G.edges(u=2, begin=11)
        [(2, 4, 11), (2, 4, 15)]
        >>> G.edges(u=2, v=4, end=11)
        [(2, 4, 11)]
        >>> G.edges(u=1, v=6)
        []

        To get a list of edges with data:

        >>> G = dnx.ImpulseDiGraph()
        >>> G.add_edge(1, 3, 4, weight=8, height=18)
        >>> G.add_edge(1, 2, 10, weight=10)
        >>> G.add_edge(2, 6, 10)
        >>> G.edges(data="weight")
        [((1, 3, 4), 8), ((1, 2, 10), 10), ((2, 6, 10), None)]
        >>> G.edges(data="weight", default=5)
        [((1, 3, 4), 8), ((1, 2, 10), 10), ((2, 6, 10), 5)]
        >>> G.edges(data=True)
        [((1, 3, 4), {'weight': 8, 'height': 18}), ((1, 2, 10), {'weight': 10}), ((2, 6, 10), {})]
        >>> G.edges(u=1, begin=2, end=9, data="weight")
        [((1, 3, 4), 8)]
        """

        if begin is None:
            inclusive = (True, inclusive[1])
        if end is None:
            inclusive = (inclusive[0], True)

        if not u and not v:
            if not begin or not end:
                iedges = [iv for iv in self.__search_tree(begin, end, inclusive)]
            # interval filtering
            else:
                if begin and end and begin > end:
                    raise NetworkXError("IntervalGraph: interval end must be bigger than or equal to begin: "
                                        "begin: {}, end: {}.".format(begin, end))
                iedges = [iv for iv in self.__search_tree(begin, end, inclusive)]

        else:
            # Node filtering
            if u and v:
                if u not in self._pred:
                    return []
                if v not in self._pred[u]:
                    return []
                iedges = self._pred[u][v]

            elif u is not None:
                if u not in self._pred:
                    return []
                iedges = [iv for v in self._pred[u] for iv in self._pred[u][v]]
            else:
                if v not in self._succ:
                    return []
                iedges = [iv for u in self._succ[v] for iv in self._succ[v][u]]

            # Interval filtering
            if begin and end and begin > end:
                raise NetworkXError("IntervalGraph: interval end must be bigger than or equal to begin: "
                                    "begin: {}, end: {}.".format(begin, end))
            iedges = [iv for iv in iedges if self.__in_interval(iv[2], begin, end, inclusive=inclusive)]

        if data is False:
            return [edge for edge in iedges]

        if data is True:
            return [(edge, self._pred[edge[0]][edge[1]][edge]) for edge in iedges]
        return [(edge, self._pred[edge[0]][edge[1]][edge][data]) if data in self._pred[edge[0]][edge[1]][edge] else (edge, default) for edge in iedges]

    def remove_edge(self, u, v, begin=None, end=None, inclusive=(True, True)):
        """Remove the edge between u and v in the impulse graph,
        during the given interval.

        Quiet if the specified edge is not present.

        Parameters
        ----------
        u, v : nodes
            Nodes can be, for example, strings or numbers.
            Nodes must be hashable (and not None) Python objects.
        begin : int or float, optional (default= beginning of the entire impulse graph)
        end : int or float, optional (default= end of the entire impulse graph + 1)
            Must be bigger than or equal to begin.
        inclusive: 2-tuple boolean that determines inclusivity of begin and end

        Examples
        --------
        >>> G = dnx.ImpulseDiGraph()
        >>> G.add_edges_from([(1, 2, 10), (2, 4, 11), (6, 4, 9), (1, 2, 15)])
        >>> G.remove_edge(1, 2)
        >>> G.has_edge(1, 2)
        False

        >>> G = dnx.ImpulseDiGraph()
        >>> G.add_edges_from([(1, 2, 10), (2, 4, 11), (6, 4, 9), (1, 2, 15)])
        >>> G.remove_edge(1, 2, begin=2, end=11)
        >>> G.has_edge(1, 2, begin=2, end=11)
        False
        >>> G.has_edge(1, 2)
        True
        """

        if u not in self._pred or v not in self._pred[u]:
            return

        iedges_to_remove = []

        # remove every edge between u and v
        if begin is None and end is None:
            for iv in self._pred[u][v]:
                iedges_to_remove.append(iv)

        else:
            for iv in self._pred[u][v]:
                if self.__in_interval(iv[2], begin, end):
                    iedges_to_remove.append(iv)

        # removing found iedges
        for edge in iedges_to_remove:
            self.__remove_iedge(edge)

        # clean up empty dictionaries
        if len(self._pred[u][v]) == 0:
            self._pred[u].pop(v, None)
        if len(self._succ[v][u]) == 0:
            self._succ[v].pop(u, None)
        if len(self._pred[u]) == 0:
            self._pred.pop(u, None)
        if len(self._succ[v]) == 0:
            self._succ.pop(v, None)

    def degree(self, node=None, begin=None, end=None, delta=False, inclusive=(True, True)):
        """Return the sum of in and out degree of a specified node between time begin and end.

        Parameters
        ----------
        node : Nodes can be, for example, strings or numbers.
            Nodes must be hashable (and not None) Python objects.
        begin : int or float, optional (default= beginning of the entire impulse graph)
            Inclusive beginning time of the edge appearing in the impulse graph.
        end : int or float, optional (default= end of the entire impulse graph)
            Non-inclusive ending time of the edge appearing in the impulse graph.
        delta : boolean, optional (default= False)
            Returns list of 2-tuples, first element is the timestamp, second is the node of changing degree.
        inclusive : 2-tuple boolean that determines inclusivity of begin and end

        Returns
        -------
        Integer value of degree of specified node.

        Examples
        --------
        >>> G = dnx.ImpulseDiGraph()
        >>> G.add_edge(1, 2, 3)
        >>> G.add_edge(2, 3, 8)
        >>> G.degree(2)
        2
        >>> G.degree(2, 4)
        1
        >>> G.degree(2, end=8)
        2
        >>> G.degree()
        1.33333
        >>> G.degree(2, delta=True)
        [(3, 1), (8, 1)]
        """
        # no specified node, return mean degree
        if node == None:
            n = 0
            l = 0
            for node in self.nodes(begin=begin, end=end, inclusive=inclusive):
                n += 1
                l += self.degree(node, begin=begin, end=end, inclusive=inclusive)
            return l / n

        # specified node, no degree_change, return degree
        if delta == False:
            return len(self.edges(u=node, begin=begin, end=end, inclusive=inclusive)) + \
                   len(self.edges(v=node, begin=begin, end=end, inclusive=inclusive))

        # delta == True, return list of changes
        if begin == None:
            begin = list(self.tree.keys())[0]
        if end == None:
            end = list(self.tree.keys())[-1]

        d = {}
        output = []

        # for each edge determine if the begin and/or end value is in specified time period
        for edge in self.edges(u=node, begin=begin, end=end, inclusive=(True, True)):
            d.setdefault(edge[2], []).append((edge[0], edge[1]))
        for edge in self.edges(v=node, begin=begin, end=end, inclusive=(True, True)):
            d.setdefault(edge[2], []).append((edge[0], edge[1]))

        # for each time in Dict add to output list the len of each value
        for time in d:
            output.append((time, len(d[time])))

        return sorted(output)

    def in_degree(self, node=None, begin=None, end=None, delta=False, inclusive=(True, True)):
        """Return the in-degree of a specified node between time begin and end.

        Parameters
        ----------
        node : Nodes can be, for example, strings or numbers.
            Nodes must be hashable (and not None) Python objects.
        begin : int or float, optional (default= beginning of the entire impulse graph)
            Inclusive beginning time of the edge appearing in the impulse graph.
        end : int or float, optional (default= end of the entire impulse graph)
            Non-inclusive ending time of the edge appearing in the impulse graph.
        delta : boolean, optional (default= False)
            Returns list of 2-tuples, first element is the timestamp, second is the node of changing degree.
        inclusive : 2-tuple boolean that determines inclusivity of begin and end

        Returns
        -------
        Integer value of in-degree of specified node.

        Examples
        --------
        >>> G = dnx.ImpulseDiGraph()
        >>> G.add_edge(1, 2, 3)
        >>> G.add_edge(2, 3, 8)
        >>> G.in_degree(2)
        1
        >>> G.in_degree(2, 4)
        0
        >>> G.in_degree(2, end=8)
        1
        >>> G.in_degree()
        0.66666
        >>> G.in_degree(2, delta=True)
        [(3, 1)]
        """
        # no specified node, return mean degree
        if node == None:
            n = 0
            l = 0
            for node in self.nodes(begin=begin, end=end, inclusive=inclusive):
                n += 1
                l += self.in_degree(node, begin=begin, end=end, inclusive=inclusive)
            return l / n

        # specified node, no degree_change, return degree
        if delta == False:
            return len(self.edges(v=node, begin=begin, end=end, inclusive=inclusive))

        # delta == True, return list of changes
        if begin == None:
            begin = list(self.tree.keys())[0]
        if end == None:
            end = list(self.tree.keys())[-1]

        d = {}
        output = []

        # for each edge determine if the begin and/or end value is in specified time period
        for edge in self.edges(v=node, begin=begin, end=end, inclusive=(True, True)):
            d.setdefault(edge[2], []).append((edge[0], edge[1]))

        # for each time in Dict add to output list the len of each value
        for time in d:
            output.append((time, len(d[time])))

        return output

    def out_degree(self, node=None, begin=None, end=None, delta=False, inclusive=(True, True)):
        """Return the out-degree of a specified node between time begin and end.

        Parameters
        ----------
        node : Nodes can be, for example, strings or numbers.
            Nodes must be hashable (and not None) Python objects.
        begin : int or float, optional (default= beginning of the entire impulse graph)
            Inclusive beginning time of the edge appearing in the impulse graph.
        end : int or float, optional (default= end of the entire impulse graph)
            Non-inclusive ending time of the edge appearing in the impulse graph.
        delta : boolean, optional (default= False)
            Returns list of 2-tuples, first element is the timestamp, second is the node of changing degree.
        inclusive : 2-tuple boolean that determines inclusivity of begin and end

        Returns
        -------
        Integer value of out-degree of specified node.

        Examples
        --------
        >>> G = dnx.ImpulseDiGraph()
        >>> G.add_edge(1, 2, 3)
        >>> G.add_edge(2, 3, 8)
        >>> G.out_degree(2)
        1
        >>> G.out_degree(2, 2)
        1
        >>> G.out_degree(2, end=8)
        1
        >>> G.out_degree()
        0.66666
        >>> G.out_degree(2, delta=True)
        [(8, 1)]
        """
        # no specified node, return mean degree
        if node == None:
            n = 0
            l = 0
            for node in self.nodes(begin=begin, end=end, inclusive=inclusive):
                n += 1
                l += self.in_degree(node, begin=begin, end=end, inclusive=inclusive)
            return l / n

        # specified node, no degree_change, return degree
        if delta == False:
            return len(self.edges(u=node, begin=begin, end=end, inclusive=inclusive))

        # delta == True, return list of changes
        if begin == None:
            begin = list(self.tree.keys())[0]
        if end == None:
            end = list(self.tree.keys())[-1]

        d = {}
        output = []

        # for each edge determine if the begin and/or end value is in specified time period
        for edge in self.edges(u=node, begin=begin, end=end, inclusive=(True, True)):
            d.setdefault(edge[2], []).append((edge[0], edge[1]))

        # for each time in Dict add to output list the len of each value
        for time in d:
            output.append((time, len(d[time])))

        return output

    def to_networkx_graph(self, begin=None, end=None, inclusive=(True, False), multigraph=False, edge_data=False,
                          edge_timestamp_data=False, node_data=False):
        """Return a networkx Graph or MultiGraph which includes all the nodes and
        edges which have timestamps within the given interval.

        Wrapper function for ImpulseGraph.to_subgraph. Refer to ImpulseGraph.to_subgraph for full description.
        """
        return self.to_subgraph(begin=begin, end=end, inclusive=inclusive, multigraph=multigraph, edge_data=edge_data,
                                edge_timestamp_data=edge_timestamp_data, node_data=node_data)

    def to_subgraph(self, begin, end, inclusive=(True, False), multigraph=False, edge_data=False,
                    edge_timestamp_data=False, node_data=False):
        """Return a networkx Graph or MultiGraph which includes all the nodes and
        edges which have timestamps within the given interval.

        Parameters
        ----------
        begin: int or float
        end: int or float
            Must be bigger than or equal to begin.
        inclusive: 2-tuple boolean that determines inclusivity of begin and end
        multigraph: bool, optional (default= False)
            If True, a networkx MultiGraph will be returned. If False, networkx Graph.
        edge_data: bool, optional (default= False)
            If True, edges will keep their attributes.
        edge_timestamp_data: bool, optional (default= False)
            If True, each edge's attribute will also include its timestamp data.
            If `edge_data= True` and there already exist edge attributes named timestamp
            it will be overwritten.
        node_data : bool, optional (default= False)
            if True, each node's attributes will be included.

        See Also
        --------
        to_snapshots : divide the impulse graph to snapshots

        Notes
        -----
        If multigraph= False, and edge_data=True or edge_interval_data=True,
        in case there are multiple edges, only one will show with one of the edge's attributes.

        Note: nodes with no edges will not appear in any subgraph.

        Examples
        --------
        >>> G = dnx.ImpulseGraph()
        >>> G.add_edges_from([(1, 2, 10), (2, 4, 11), (6, 4, 19), (2, 4, 15)])
        >>> H = G.to_subgraph(4, 12)
        >>> type(H)
        <class 'networkx.classes.graph.DiGraph'>
        >>> list(H.edges(data=True))
        [(1, 2, {}), (2, 4, {})]

        >>> H = G.to_subgraph(10, 12, edge_timestamp_data=True)
        >>> type(H)
        <class 'networkx.classes.graph.DiGraph'>
        >>> list(H.edges(data=True))
        [(1, 2, {'timestamp': 10}), (2, 4, {'timestamp': 11})]

        >>> M = G.to_subgraph(4, 12, multigraph=True, edge_timestamp_data=True)
        >>> type(M)
        <class 'networkx.classes.multigraph.MultiDiGraph'>
        >>> list(M.edges(data=True))
        [(1, 2, {'timestamp': 10}), (2, 4, {'timestamp': 11})]
        """
        iedges = self.__search_tree(begin, end, inclusive=inclusive)

        if multigraph:
            G = MultiDiGraph()
        else:
            G = DiGraph()

        if edge_data and edge_timestamp_data:
            G.add_edges_from((iedge[0], iedge[1], dict(self._pred[iedge[0]][iedge[1]][iedge], timestamp=iedge[3]))
                             for iedge in iedges)
        elif edge_data:
            G.add_edges_from((iedge[0], iedge[1], self._pred[iedge[0]][iedge[1]][iedge])
                             for iedge in iedges)
        elif edge_timestamp_data:
            G.add_edges_from((iedge[0], iedge[1], {'timestamp': iedge[3]})
                             for iedge in iedges)
        else:

            G.add_edges_from((iedge[0], iedge[1]) for iedge in iedges)

        if node_data:
            G.add_nodes_from((n, self._node[n].copy()) for n in G.nodes)

        return G

    def __remove_iedge(self, iedge):
        """Remove the impulse edge from the impulse graph.

        Quiet if the specified edge is not present.

        Parameters
        ----------
        iedge : Edge Tuple (u,v,eid,t)
            Edge to be removed.
        """

        try:
            self.tree[iedge[2]].remove((iedge[0], iedge[1]))
            del self._pred[iedge[0]][iedge[1]][iedge]
            del self._succ[iedge[1]][iedge[0]][iedge]
        except:
            return

    def __validate_interval(self, begin=None, end=None):
        """Returns validated begin and end.
        Raises an exception if begin is larger than end.

        Parameters
        ----------
        begin : int or float, optional
        end : int or float, optional
        """

        if (begin is not None and end is not None) and begin > end:
            raise NetworkXError("ImpulseDiGraph: interval end must be bigger than or equal to begin: "
                                "begin: {}, end: {}.".format(begin, end))

        return begin, end

    def __search_tree(self, begin=None, end=None, inclusive=(True, True)):
        """if begin and end are equal performs a point search on the tree,
        otherwise an interval search is performed.

       Parameters
       ----------
       begin: int or float, optional  (default= beginning of the entire impulse graph)
       end: int or float, optional  (default= end of the entire impulse graph)
            Must be bigger than or equal begin.
       inclusive: 2-tuple boolean that determines inclusivity of begin and end
       """
        begin, end = self.__validate_interval(begin, end)

        if begin is not None and begin == end and begin in self.tree:
            for edge in self.tree[begin]:
                yield (*edge, begin)

        for t in self.tree.irange(begin, end, inclusive=inclusive):
            for edge in self.tree[t]:
                yield (*edge, t)

    def __in_interval(self, t, begin, end, inclusive=(True, True)):
        """
        Parameters
        ----------
        t: int or float, timestamp
        begin: int or float
            Beginning time of Interval.
        end: int or float
            Ending time of Interval.
            Must be bigger than or equal begin.
        inclusive: 2-tuple boolean that determines inclusivity of begin and end

        Returns
        -------
        Returns True if t is in the interval (begin,end). Otherwise False.
        """
        if begin is None:
            begin = float('-inf')
        if end is None:
            end = float('inf')

        if inclusive == (True, True):
            return begin <= t <= end
        if inclusive == (True, False):
            return begin <= t < end
        if inclusive == (False, True):
            return begin < t <= end
        if inclusive == (False, False):
            return begin < t < end

    @staticmethod
    def load_from_txt(path, delimiter=" ", nodetype=int, timestamptype=float, order=('u', 'v', 't'), comments="#"):
        """Read impulse graph in from path.
           Timestamps must be integers or floats.
           Nodes can be any hashable objects.
           Edge Attributes can be assigned with in the following format: Key=Value

        Parameters
        ----------
        path : string or file
           Filename to read.

        nodetype : Python type, optional (default= int)
           Convert nodes to this type.

        timestamptype : Python type, optional (default= float)
        Convert timestamp to this type.
        This must be an orderable type, ideally int or float. Other orderable types have not been fully tested.

        order : Python 3-tuple, optional (default= ('u', 'v', 't'))
        This must be a 3-tuple containing strings 'u', 'v', and 't'. 'u' specifies the starting node, 'v' the ending node, and 't' the timestamp.

        comments : string, optional
           Marker for comment lines

        delimiter : string, optional
           Separator for node labels.  The default is whitespace. Cannot be =.

        Returns
        -------
        G: ImpulseGraph
            The graph corresponding to the lines in edge list.

        Examples
        --------
        >>> G=dnx.ImpulseGraph.load_from_txt("my_dygraph.txt")

        The optional nodetype is a function to convert node strings to nodetype.

        For example

        >>> G=dnx.ImpulseGraph.load_from_txt("my_dygraph.txt", nodetype=int)

        will attempt to convert all nodes to integer type.

        Since nodes must be hashable, the function nodetype must return hashable
        types (e.g. int, float, str, frozenset - or tuples of those, etc.)
        """

        G = ImpulseDiGraph()

        if delimiter == '=':
            raise ValueError("Delimiter cannot be =.")

        if len(order) != 3 or 'u' not in order or 'v' not in order or 't' not in order:
            raise ValueError("Order must be a 3-tuple containing strings 'u', 'v', and 't'.")

        with open(path, 'r') as file:
            for line in file:
                p = line.find(comments)
                if p >= 0:
                    line = line[:p]
                if not len(line):
                    continue

                line = re.split(delimiter+'+', line.strip())

                u = line[order.index('u')]
                v = line[order.index('v')]
                t = line[order.index('t')]

                edgedata = {}
                for data in line[3:]:
                    key, value = data.split('=')

                    try:
                        value = float(value)
                    except:
                        pass
                    edgedata[key] = value

                if nodetype is not int:
                    try:
                        u = nodetype(u)
                        v = nodetype(v)
                    except:
                        raise TypeError("Failed to convert node to {0}".format(nodetype))
                else:
                    try:
                        u = int(u)
                        v = int(v)
                    except:
                        pass

                try:
                    t = timestamptype(t)
                except:
                    raise TypeError("Failed to convert interval time to {}".format(timestamptype))

                G.add_edge(u, v, t, **edgedata)

        return G

    def enumerate_subgraphs(self, g, size_k):
        # vertices = sorted(g.nodes())
        for v in g.nodes():
            v_extension = set(filter(lambda x: x > v, g.neighbors(v)))
            yield from self.__extend_subgraph({v}, v_extension, v, g, size_k)

    def __extend_subgraph(self, v_subgraph, v_extension, v, g, size_k):
        if len(v_subgraph) == size_k:
            yield g.subgraph(v_subgraph)
        else:
            while len(v_extension) != 0:
                w = random.choice(tuple(v_extension))
                v_extension.remove(w)

                v2_extension = v_extension.copy().union(set(filter(lambda x: x > v,
                                                                   set(g.neighbors(w)) - v_subgraph)))
                yield from self.__extend_subgraph(v_subgraph.copy().union({w}), v2_extension, v, g, size_k)

    def calculate_temporal_motifs(self, sequence, delta, get_count_dict=False):
        total_counts = dict()
        # this is used later for checking matching sequences
        node_sequence = tuple(node for edge in sequence for node in edge)
        g = Graph(self.to_networkx_graph())
        static_motif = Graph()
        static_motif.add_edges_from(sequence)

        for sub in self.enumerate_subgraphs(g, size_k=len(static_motif.nodes())):
            # A way to check if nodes in sub may contain motif will help speed up. Using nx.is_isomorphic() will
            # create error by dropping a lot of potential subgraphs.
            counts = dict()
            edges = list()
            for u, v in itertools.combinations(sub.nodes(), 2):
                edges.extend(self.edges(u, v))
                edges.extend(self.edges(v, u))

            # Motifs with self-loops won't be duplicated when iterating through subgraphs
            for u in sub.nodes():
                edges.extend(self.edges(u, u))

            edges = sorted(edges, key=lambda x: x[2])
            # Count all possible sequences from edges of the static subgraph
            start = 0
            end = 0
            while end < len(edges):
                while edges[start][2] + delta < edges[end][2]:

                    # combine all edges having the same timestamps to decrement counts
                    tmp_time = edges[start][2]
                    same_time_edges = list()

                    while edges[start][2] == tmp_time:
                        same_time_edges.append(edges[start][0:2])
                        start += 1
                        if start >= len(edges):
                            break
                    self.__decrement_counts(same_time_edges, len(sequence), counts)

                # combine all edges having the same timestamps to increment counts
                tmp_time = edges[end][2]
                same_time_edges = list()
                while edges[end][2] == tmp_time:
                    same_time_edges.append(edges[end][0:2])
                    end += 1
                    if end >= len(edges):
                        break

                self.__increment_counts(same_time_edges, len(sequence), counts)

            # Extract out count for sequences that are isomorphic to the temporal motifs
            for keys in sorted(counts.keys()):
                if len(keys)/2 == len(sequence):
                    if counts[keys] == 0:
                        continue

                    node_map = dict()
                    isomorphic = True
                    # check matching sequences (node sequence vs key)
                    for n in range(len(node_sequence)):
                        if node_map.get(node_sequence[n]):
                            if node_map[node_sequence[n]] == keys[n]:
                                continue
                            else:
                                isomorphic = False
                                break
                        else:
                            if not keys[n] in node_map.values():
                                node_map[node_sequence[n]] = keys[n]
                            else:
                                isomorphic = False
                                break
                    if isomorphic:
                        total_counts[keys] = counts[keys]

        if get_count_dict:
            return total_counts
        else:
            return sum(total_counts.values())

    @staticmethod
    def __decrement_counts(edges, motif_length, counts):

        suffixes = sorted(counts.keys(), key=len)
        for e in edges:
            counts[e] -= 1

        for suffix in suffixes:
            if len(suffix)/2 < motif_length - 1:
                for e in edges:
                    if counts.get(e + suffix):
                        counts[e + suffix] -= counts[suffix]

    @staticmethod
    def __increment_counts(edges, motif_length, counts):

        prefixes = sorted(counts.keys(), key=len, reverse=True)
        for prefix in prefixes:
            if len(prefix)/2 < motif_length:
                for e in edges:
                    if counts.get(prefix + e) is None:
                        counts[prefix + e] = 0
                    counts[prefix + e] += counts[prefix]

        for e in edges:
            if counts.get(e) is None:
                counts[e] = 0
            counts[e] += 1
