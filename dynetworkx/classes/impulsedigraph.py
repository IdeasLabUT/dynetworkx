from dynetworkx.classes.impulsegraph import ImpulseGraph
from networkx.classes.graph import Graph
from networkx.exception import NetworkXError
from sortedcontainers import SortedDict, SortedList
from networkx.classes.multigraph import MultiGraph
from networkx.classes.reportviews import NodeView, EdgeView, NodeDataView


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

        eid = self.edgeid
        self.tree.setdefault(t, set()).add((u, v, eid))

        self._node.setdefault(u, {})
        self._node.setdefault(v, {})
        self._pred.setdefault(u, {})[(u, v, eid, t)] = attr
        self._succ.setdefault(v, {})[(u, v, eid, t)] = attr

        self.edgeid += 1

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

        if begin is None and end is None:
            for edge in self._pred[u].keys():
                if edge[1] == v:
                    return True
            return False

        begin, end = self.__validate_interval(begin, end)

        for edge in self._pred[u].keys():
            if edge[1] == v and self.__in_interval(edge[3], begin, end, inclusive=inclusive):
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

        iedges = []
        for edge in self.__search_tree(begin, end, inclusive=inclusive):
            if u is not None and v is not None and u == edge[0] and v == edge[1]:
                iedges.append(edge)
            elif (u is not None and v is None) and u == edge[0]:
                iedges.append(edge)
            elif (u is None and v is not None) and v == edge[1]:
                iedges.append(edge)
            elif u is None and v is None:
                iedges.append(edge)

        if data is False:
            return [(edge[0], edge[1], edge[3]) for edge in iedges]

        if data is True:
            return [((edge[0], edge[1], edge[3]), self._pred[edge[0]][edge]) for edge in iedges]

        return [((edge[0], edge[1], edge[3]), self._pred[edge[0]][edge][data]) if data in self._pred[edge[0]][edge]
                else ((edge[0], edge[1], edge[3]), default) for edge in iedges]

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

        iedges = []
        for edge in self.__search_tree(begin, end, inclusive=inclusive):
            if u == edge[0] and v == edge[1]:
                iedges.append(edge)

        for edge in iedges:
            self.__remove_iedge(edge)

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

    def __remove_iedge(self, iedge):
        """Remove the impulse edge from the impulse graph.

        Quiet if the specified edge is not present.

        Parameters
        ----------
        iedge : Edge Tuple (u,v,eid,t)
            Edge to be removed.
        """

        u = iedge[0]
        v = iedge[1]
        eid = iedge[2]
        t = iedge[3]

        try:
            self.tree[t].remove((u, v, eid))
            del self._pred[u][iedge]
            del self._succ[v][iedge]
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