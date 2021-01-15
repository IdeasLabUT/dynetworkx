import dynetworkx as dnx
from networkx.classes.graph import Graph
from networkx.exception import NetworkXError
from dynetworkx.classes.intervaltree import IntervalTree
from networkx.classes.multigraph import MultiGraph
from networkx.classes.reportviews import NodeView, EdgeView, NodeDataView
from sortedcontainers import SortedList, SortedDict


class IntervalGraph(object):
    """Base class for undirected interval graphs.

    The IntervalGraph class allows any hashable object as a node
    and can associate key/value attribute pairs with each undirected edge.

    Each edge must have two integers, begin and end for its interval.

    Self-loops are allowed but multiple edges
    (two or more edges with the same nodes, begin and end interval) are not.

    Two nodes can have more than one edge with different overlapping or non-overlapping intervals.

    Parameters
    ----------
    attr : keyword arguments, optional (default= no attributes)
        Attributes to add to graph as key=value pairs.

    Examples
    --------
    Create an empty graph structure (a "null interval graph") with no nodes and
    no edges.

    >>> G = dnx.IntervalGraph()

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

    Add one edge, which starts at 0 and ends at 10.
    Keep in mind that the interval is [0, 10).
    Thus, it does not include the end.

    >>> G.add_edge(1, 2, 0, 10)

    a list of edges,

    >>> G.add_edges_from([(1, 2, 0, 10), (1, 3, 3, 11)])

    If some edges connect nodes not yet in the graph, the nodes
    are added automatically. There are no errors when adding
    nodes or edges that already exist.

    **Attributes:**

    Each interval graph, node, and edge can hold key/value attribute pairs
    in an associated attribute dictionary (the keys must be hashable).
    By default these are empty, but can be added or changed using
    add_edge, add_node.

    Keep in mind that the edge interval is not an attribute of the edge.

    >>> G = dnx.IntervalGraph(day="Friday")
    >>> G.graph
    {'day': 'Friday'}

    Add node attributes using add_node(), add_nodes_from()

    >>> G.add_node(1, time='5pm')
    >>> G.add_nodes_from([3], time='2pm')

    Add edge attributes using add_edge(), add_edges_from().

    >>> G.add_edge(1, 2, 0, 10, weight=4.7 )
    >>> G.add_edges_from([(3, 4, 3, 11), (4, 5, 0, 33)], color='red')

    **Shortcuts:**

    Here are a couple examples of available shortcuts:

    >>> 1 in G  # check if node in interval graph during any interval
    True
    >>> len(G)  # number of nodes in the entire interval graph
    5

    **Subclasses (Advanced):**
    Edges in interval graphs are represented by Interval Objects and are kept
    in an IntervalTree. Both are based on
    intervaltree available in pypi (https://pypi.org/project/intervaltree).
    IntervalTree allows for fast interval based search through edges,
    which makes interval graph analysis possible.

    The Graph class uses a dict-of-dict-of-dict data structure.
    The outer dict (node_dict) holds adjacency information keyed by nodes.
    The next dict (adjlist_dict) represents the adjacency information and holds
    edge data keyed by interval objects. The inner dict (edge_attr_dict) represents
    the edge data and holds edge attribute values keyed by attribute names.
    """

    def __init__(self, **attr):
        """Initialize an interval graph with edges, name, or graph attributes.

        Parameters
        ----------
        attr : keyword arguments, optional (default= no attributes)
            Attributes to add to graph as key=value pairs.

        Examples
        --------
        >>> G = dnx.IntervalGraph()
        >>> G = dnx.IntervalGraph(name='my graph')
        >>> G.graph
        {'name': 'my graph'}
        """
        self.tree = IntervalTree()
        self.graph = {}  # dictionary for graph attributes
        self._node = {}
        self._adj = {}

        self.graph.update(attr)

    @property
    def name(self):
        """String identifier of the interval graph.

        This interval graph attribute appears in the attribute dict IG.graph
        keyed by the string `"name"`. as well as an attribute (technically
        a property) `IG.name`. This is entirely user controlled.
        """
        return self.graph.get('name', '')

    @name.setter
    def name(self, s):
        self.graph['name'] = s

    def __str__(self):
        """Return the interval graph name.

        Returns
        -------
        name : string
            The name of the interval graph.

        Examples
        --------
        >>> G = dnx.IntervalGraph(name='foo')
        >>> str(G)
        'foo'
        """
        return self.name

    def __len__(self):
        """Return the number of nodes. Use: 'len(G)'.

        Returns
        -------
        nnodes : int
            The number of nodes in the graph.

        Examples
        --------
        >>> G = dnx.IntervalGraph()
        >>> G.add_nodes_from([2, 4, 5])
        >>> len(G)
        3

        """
        return len(self._node)

    def __contains__(self, n):
        """Return True if n is a node, False otherwise. Use: 'n in G'.

        Examples
        --------
        >>> G = dnx.IntervalGraph()
        >>> G.add_node(2)
        >>> 2 in G
        True
        """
        try:
            return n in self._node
        except TypeError:
            return False

    def interval(self):
        """Return a 2-tuple as (begin, end) interval of the entire
         interval graph.

         Note that end is non-inclusive.

        Examples
        --------
        >>> G = dnx.IntervalGraph()
        >>> G.add_edges_from([(1, 2, 0, 10), (3, 7, 9, 16)])
        >>> G.interval()
        (0, 16)
        """
        return self.tree.begin, self.tree.end

    def add_node(self, node_for_adding, **attr):
        """Add a single node `node_for_adding` and update node attributes.

        Parameters
        ----------
        node_for_adding : node
            A node can be any hashable Python object except None.
        attr : keyword arguments, optional
            Set or change node attributes using key=value.

        See Also
        --------
        add_nodes_from

        Examples
        --------
        >>> G = dnx.IntervalGraph()
        >>> G.add_node(1)
        >>> G.add_node('Hello')
        >>> G.number_of_nodes()
        2

        Use keywords set/change node attributes:

        >>> G.add_node(1, size=10)
        >>> G.add_node(3, weight=0.4, UTM=('13S', 382871, 3972649))

        Notes
        -----
        A hashable object is one that can be used as a key in a Python
        dictionary. This includes strings, numbers, tuples of strings
        and numbers, etc.

        On many platforms hashable items also include mutables such as
        NetworkX Graphs, though one should be careful that the hash
        doesn't change on mutables.
        """
        self._node.setdefault(node_for_adding, attr).update(attr)
        self._adj.setdefault(node_for_adding, {})

    def add_nodes_from(self, nodes_for_adding, **attr):
        """Add multiple nodes.

        Parameters
        ----------
        nodes_for_adding : iterable container
            A container of nodes (list, dict, set, etc.).
            OR
            A container of (node, attribute dict) tuples.
            Node attributes are updated using the attribute dict.
        attr : keyword arguments, optional (default= no attributes)
            Update attributes for all nodes in nodes.
            Node attributes specified in nodes as a tuple take
            precedence over attributes specified via keyword arguments.

        See Also
        --------
        add_node

        Examples
        --------
        >>> G = dnx.IntervalGraph()
        >>> G.add_nodes_from('Hello')
        >>> G.has_node('e')
        True

        Use keywords to update specific node attributes for every node.

        >>> G.add_nodes_from([1, 2], size=10)
        >>> G.add_nodes_from([3, 4], weight=0.4)

        Use (node, attrdict) tuples to update attributes for specific nodes.

        >>> G.add_nodes_from([(1, dict(size=11)), (2, {'color':'blue'})])
        """
        for n in nodes_for_adding:
            if isinstance(n, tuple) and isinstance(n[1], dict):
                self.add_node(n[0], **attr)
                self._node[n[0]].update(n[1])
            else:
                self.add_node(n, **attr)
        '''
        for n in nodes_for_adding:
            # keep all this inside try/except because
            # CPython throws TypeError on n not in self._node,
            # while pre-2.7.5 ironpython throws on self._adj[n]
            try:
                if n not in self._node:
                    self._adj[n] = {}
                    self._node[n] = attr.copy()
                else:
                    self._node[n].update(attr)
            except TypeError:
                nn, ndict = n
                if nn not in self._node:
                    self._adj[nn] = {}
                    self._node[nn] = attr.copy()
                    self._node[nn].update(ndict)
                else:
                    self._node[nn].update(attr)
                    self._node[nn].update(ndict)
        '''

    def number_of_nodes(self, begin=None, end=None):
        """Return the number of nodes in the interval graph between the given interval.

        Parameters
        ----------
        begin: int or float, optional (default= beginning of the entire interval graph)
            Inclusive beginning time of the node appearing in the interval graph.
        end: int or float, optional  (default= end of the entire interval graph + 1)
            Non-inclusive ending time of the node appearing in the interval graph.
            Must be bigger than or equal begin.
            Note that the default value is shifted up by 1 to make it an inclusive end.

        Returns
        -------
        nnodes : int
            The number of nodes in the interval graph.

        See Also
        --------
        __len__

        Examples
        --------
        >>> G = dnx.IntervalGraph()
        >>> G.add_edges_from([(1, 2, 0, 5), (3, 4, 8, 11)])
        >>> len(G)
        4
        >>> G.number_of_nodes()
        4
        >>> G.number_of_nodes(begin=6)
        2
        >>> G.number_of_nodes(begin=5, end=8) # end in non-inclusive
        2
        >>> G.number_of_nodes(end=8)
        4
        """

        if begin is None and end is None:
            return len(self._node)

        iedges = self.tree[begin:end]

        inodes = set()
        for u, v, _, _ in iedges:
            inodes.add(u)
            inodes.add(v)

        return len(inodes)

    def has_node(self, n, begin=None, end=None):
        """Return True if the interval graph contains the node n, during the given interval.

        Identical to `n in G` when 'begin' and 'end' are not defined.

        Parameters
        ----------
        n : node
        begin: int or float, optional  (default= beginning of the entire interval graph)
            Inclusive beginning time of the node appearing in the interval graph.
        end: int or float, optional  (default= end of the entire interval graph + 1)
            Non-inclusive ending time of the node appearing in the interval graph.
            Must be bigger than or equal begin.
            Note that the default value is shifted up by 1 to make it an inclusive end.

        Examples
        --------
        >>> G = dnx.IntervalGraph()
        >>> G.add_node(1)
        >>> G.has_node(1)
        True

        It is more readable and simpler to use

        >>> 0 in G
        True

        With interval query:

        >>> G.add_edge(3, 4, 2, 5)
        >>> G.has_node(3)
        True
        >>> G.has_node(3, begin=2)
        True
        >>> G.has_node(3, end=2) # end is non-inclusive
        False
        """

        if n not in self._node:
            return False

        if begin is None and end is None:
            return True

        if begin is None and end < self.tree.begin:
            return False

        if begin is not None and end is not None and end < begin:
            return False

        if begin and end and begin > end:
            raise NetworkXError("IntervalGraph: interval end must be bigger than or equal to begin: "
                                "begin: {}, end: {}.".format(begin, end))

        for edge in self.tree[begin:end]:
            if n == edge[0] or n == edge[1]:
                return True
        return False

    def nodes(self, begin=None, end=None, data=False, default=None):
        """A NodeDataView of the IntervalGraph nodes.

        A nodes is considered to be present during an interval, if it has
        an edge with overlapping interval.

        Parameters
        ----------
        begin: int or float, optional  (default= beginning of the entire interval graph)
            Inclusive beginning time of the node appearing in the interval graph.
        end: int or float, optional  (default= end of the entire interval graph + 1)
            Non-inclusive ending time of the node appearing in the interval graph.
            Must be bigger than or equal to begin.
            Note that the default value is shifted up by 1 to make it an inclusive end.
        data : string or bool, optional (default=False)
            The node attribute returned in 2-tuple (n, dict[data]).
            If False, return just the nodes n.
        default : value, optional (default=None)
            Value used for nodes that don't have the requested attribute.
            Only relevant if data is not True or False.

        Returns
        -------
        NodeDataView
            A NodeDataView iterates over `(n, data)` and has no set operations.

            When called, if data is False, an iterator over nodes.
            Otherwise an iterator of 2-tuples (node, attribute value)
            where data is True.

        Examples
        --------
        There are two simple ways of getting a list of all nodes in the graph:

        >>> G = dnx.IntervalGraph()
        >>> G.add_edges_from([(1, 2, 3, 10), (2, 4, 1, 11), (6, 4, 12, 19), (2, 4, 8, 15)])
        [1, 2, 4, 6]

        To get the node data along with the nodes:

        >>> G.add_nodes_from([(1, {'time': '1pm'}), (2, {'time': '2pm'}), (4, {'time': '4pm'}), (6, {'day': 'Friday'})])
        [(1, {'time': '1pm'}), (2, {'time': '2pm'}), (4, {'time': '4pm'}), (6, {'day': 'Friday'})]

        >>> G.nodes(data="time")
        [(1, '1pm'), (2, '2pm'), (4, '4pm'), (6, None)]
        >>> G.nodes(data="time", default="5pm")
        [(1, '1pm'), (2, '2pm'), (4, '4pm'), (6, '5pm')]

        To get nodes which appear in a specific interval. nodes
        without an edge are not considered present.

        >>> G.nodes(begin=11, data=True)
        [(2, {'time': '2pm'}), (4, {'time': '4pm'}), (6, {'day': 'Friday'})]
        >>> G.nodes(begin=4, end=12) # non-inclusive end
        [1, 2, 4]
        """
        if begin is None and end is None:
            return NodeDataView(self._node, data=data, default=default)

        iedges = self.tree[begin:end]

        inodes = set()
        for u, v, _, _ in iedges:
            inodes.add(u)
            inodes.add(v)

        node_dict = {n: self._node[n] for n in inodes}

        return NodeDataView(node_dict, data=data, default=default)

    def remove_node(self, n, begin=None, end=None):
        """Remove the presence of a node n within the given interval.

        Removes the presence node n and all adjacent edges within the given interval.

        If interval is specified, all the edges of n will be removed within that interval.

        Quiet if n is not in the interval graph.

        Parameters
        ----------
        n : node
           A node in the graph
        begin: int or float, optional  (default= beginning of the entire interval graph)
            Inclusive beginning time of the node appearing in the interval graph.
        end: int or float, optional  (default= end of the entire interval graph + 1)
            Non-inclusive ending time of the node appearing in the interval graph.
            Must be bigger than or equal to begin.
            Note that the default value is shifted up by 1 to make it an inclusive end.

        Examples
        --------
        >>> G.add_edges_from([(1, 2, 3, 10), (2, 4, 1, 11), (6, 4, 12, 19), (2, 4, 8, 15)])
        >>> G.add_nodes_from([(1, {'time': '1pm'}), (2, {'time': '2pm'}), (4, {'time': '4pm'})])
        >>> G.nodes(begin=4, end=6)
        [1, 2, 4, 6]
        >>> G.remove_node(2, begin=4, end=6)
        >>> G.nodes(begin=4, end=6)
        [4, 6]
        >>> G.nodes(data=True)
        [(1, {'time': '1pm'}), (2, {'time': '2pm'}), (4, {'time': '4pm'}), (6, {})]
        >>> G.remove_node(2)
        >>> G.nodes(data=True)
        [(1, {'time': '1pm'}), (4, {'time': '4pm'}), (6, {})]
        """

        if n not in self._node:
            return

        if begin is None and end is None:
            for iedge in list(self._adj[n].keys()):
                self.__remove_iedge(iedge)
        else:
            iedges = self.tree[begin:end]
            for iedge in iedges:
                if iedge[0] == n or iedge[1] == n:
                    self.__remove_iedge(iedge)

        # delete the node and its attributes if no edge left
        if len(self._adj[n]) == 0:
            self._adj.pop(n, None)
            self._node.pop(n, None)

    def add_edge(self, u, v, begin, end, **attr):
        """Add an edge between u and v, during interval [begin, end).

        The nodes u and v will be automatically added if they are
        not already in the interval graph.

        Edge attributes can be specified with keywords or by directly
        accessing the edge's attribute dictionary. See examples below.

        Parameters
        ----------
        u, v : nodes
            Nodes can be, for example, strings or numbers.
            Nodes must be hashable (and not None) Python objects.
        begin: orderable type
            Inclusive beginning time of the edge appearing in the interval graph.
        end: orderable type
            Non-inclusive ending time of the edge appearing in the interval graph.
            Must be bigger than begin.
        attr : keyword arguments, optional
            Edge data (or labels or objects) can be assigned using
            keyword arguments.

        See Also
        --------
        add_edges_from : add a collection of edges

        Notes
        -----
        Adding an edge that already exists updates the edge data.

        Both begin and end must be the same type across all edges in the interval graph. Also, to create
        snapshots, both must be integers.

        Many NetworkX algorithms designed for weighted graphs use
        an edge attribute (by default `weight`) to hold a numerical value.

        Examples
        --------
        The following all add the edge e=(1, 2, 3, 10) to graph G:

        >>> G = dnx.IntervalGraph()
        >>> e = (1, 2, 3, 10)
        >>> G.add_edge(1, 2, 3, 10)           # explicit two-node form with interval
        >>> G.add_edge(*e)             # single edge as tuple of two nodes and interval
        >>> G.add_edges_from([(1, 2, 3, 10)])  # add edges from iterable container

        Associate data to edges using keywords:

        >>> G.add_edge(1, 2, 3, 10 weight=3)
        >>> G.add_edge(1, 3, 4, 9, weight=7, capacity=15, length=342.7)
        """

        iedge = self.edges(u, v, begin, end)

        # if edge exists, just update attr
        if iedge:
            # since both point to the same attr, updating one is enough
            self._adj[u][iedge].update(attr)
            return

        iedge = (u, v, begin, end)

        # add nodes
        self._adj.setdefault(u, {})
        self._adj.setdefault(v, {})
        self._node.setdefault(u, {})
        self._node.setdefault(v, {})

        # add edge
        try:
            self.tree.add(iedge)
        except ValueError:
            raise NetworkXError("IntervalGraph: edge duration must be strictly bigger than zero {0}.".format(iedge))

        self._adj[u][iedge] = self._adj[v][iedge] = attr

    def add_edges_from(self, ebunch_to_add, **attr):
        """Add all the edges in ebunch_to_add.

        Parameters
        ----------
        ebunch_to_add : container of edges
            Each edge given in the container will be added to the
            interval graph. The edges must be given as as 4-tuples (u, v, being, end).
            Both begin and end must be orderable and the same type across all edges.
        attr : keyword arguments, optional
            Edge data (or labels or objects) can be assigned using
            keyword arguments.

        See Also
        --------
        add_edge : add a single edge

        Notes
        -----
        Adding the same edge (with the same interval) twice has no effect
        but any edge data will be updated when each duplicate edge is added.

        Examples
        --------
        >>> G = dnx.IntervalGraph()
        >>> G.add_edges_from([(1, 2, 3, 10), (2, 4, 1, 11)]) # using a list of edge tuples

        Associate data to edges

        >>> G.add_edges_from([(1, 2, 3, 10), (2, 4, 1, 11)], weight=3)
        >>> G.add_edges_from([(3, 4, 2, 19), (1, 4, 1, 3)], label='WN2898')
        """

        for e in ebunch_to_add:
            if len(e) != 4:
                raise NetworkXError("Edge tuple {0} must be a 4-tuple.".format(e))

            self.add_edge(e[0], e[1], e[2], e[3], **attr)

    def has_edge(self, u, v, begin=None, end=None, overlapping=True):
        """Return True if there exists an edge between u and v
        in the interval graph, during the given interval.

        Parameters
        ----------
        u, v : nodes
            Nodes can be, for example, strings or numbers.
            Nodes must be hashable (and not None) Python objects.
        begin : int or float, optional (default= beginning of the entire interval graph)
            Inclusive beginning time of the node appearing in the interval graph.
        end : int or float, optional (default= end of the entire interval graph + 1)
            Non-inclusive ending time of the node appearing in the interval graph.
            Must be bigger than or equal begin.
            Note that the default value is shifted up by 1 to make it an inclusive end.
        overlapping : bool, optional (default= True)
            if True, it returns True if there exists an edge between u and v with
            overlapping interval with `begin` and `end`.
            if False, it returns true only if there exists an edge between u and v
            with the exact interval.
            Note: if False, both `begin` and `end` must be defined, otherwise
            an exception is raised.

        Raises
        ------
        NetworkXError
            If `begin` and `end` are not defined and `overlapping= False`

        Examples
        --------
        >>> G = dnx.IntervalGraph()
        >>> G.add_edges_from([(1, 2, 3, 10), (2, 4, 1, 11)])
        >>> G.has_edge(1, 2)
        True

        With specific overlapping interval:
        
        >>> G.has_edge(1, 2, begin=2)
        True
        >>> G.has_edge(2, 4, begin=12)
        False

        Exact interval match:

        >>> G.has_edge(2, 4, begin=1, end=11)
        True
        >>> G.has_edge(2, 4, begin=2, end=11)
        False
        """

        if begin is None and end is None:
            for iv in self._adj[u].keys():
                if iv[0] == v or iv[1] == v:
                    return True
            return False

        if not overlapping:
            if begin is None or end is None:
                raise NetworkXError("For exact interval match (overlapping=False), both begin and end must be defined.")

            return self.edges(u, v, begin, end) is not None

        if begin and end and begin > end:
            raise NetworkXError("IntervalGraph: interval end must be bigger than or equal to begin: "
                                "begin: {}, end: {}.".format(begin, end))

        for iv in self._adj[u].keys():
            if (iv[0] == v or iv[1] == v) and self.__overlaps_or_contains(iv, begin, end):
                return True
        return False

    def edges(self, u=None, v=None, begin=None, end=None, data=False, default=None):
        """Returns a list of Interval objects of the IntervalGraph edges.

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
        begin: int or float, optional  (default= beginning of the entire interval graph)
            Inclusive beginning time of the edge appearing in the interval graph.
        end: int or float, optional  (default= end of the entire interval graph + 1)
            Non-inclusive ending time of the edge appearing in the interval graph.
            Must be bigger than or equal to begin.
            Note that the default value is shifted up by 1 to make it an inclusive end.
        data : string or bool, optional (default=False)
            If True, return 2-tuple (Interval object, dict of attributes).
            If False, return just the Interval objects.
            If string (name of the attribute), return 2-tuple (Interval object, attribute value).
        default : value, optional (default=None)
            Default Value to be used for edges that don't have the requested attribute.
            Only relevant if `data` is a string (name of an attribute).

        Returns
        -------
        List of Interval objects
            An interval object has the following format: (begin, end, (u, v))

            When called, if `data` is False, a list of interval objects.
            If `data` is True, a list of 2-tuples: (Interval, dict of attribute(s) with values),
            If `data` is a string, a list of 2-tuples (Interval, attribute value).

        Examples
        --------
        To get a list of all edges:

        >>> G = dnx.IntervalGraph()
        >>> G.add_edges_from([(1, 2, 3, 10), (2, 4, 1, 11), (6, 4, 12, 19), (2, 4, 8, 15)])
        >>> G.edges()
        [(1, 2, 3, 10), (2, 4, 1, 11), (6, 4, 12, 19), (2, 4, 8, 15)]

        To get edges which appear in a specific interval:

        >>> G.edges(begin=10)
        [(2, 4, 1, 11), (6, 4, 12, 19), (2, 4, 8, 15)]
        >>> G.edges(end=5)
        [(1, 2, 3, 10), (2, 4, 1, 11)]
        >>> G.edges(begin=2, end=4)
        [(1, 2, 3, 10), (2, 4, 1, 11)]

        To get edges with either of the two nodes being defined:

        >>> G.edges(u=2)
        [(2, 4, 1, 11), (2, 4, 8, 15)]
        >>> G.edges(u=2, begin=11)
        [(2, 4, 1, 11), (2, 4, 8, 15)]
        >>> G.edges(u=2, v=4, end=8)
        [(2, 4, 1, 11)]
        >>> G.edges(u=1, v=6)
        []

        To get a list of edges with data:

        >>> G = dnx.IntervalGraph()
        >>> G.add_edge(1, 3, 1, 4, weight=8, height=18)
        >>> G.add_edge(1, 2, 3, 10, weight=10)
        >>> G.add_edge(2, 6, 2, 10)
        >>> G.edges(data="weight")
        [((1, 3, 1, 4), 8), ((2, 6, 2, 10), None), ((1, 2, 3, 10), 10)]
        >>> G.edges(data="weight", default=5)
        [((1, 3, 1, 4), 8), ((2, 6, 2, 10), 5), ((1, 2, 3, 10), 10)]
        >>> G.edges(data=True)
        [((1, 3, 1, 4), {weight: 8, height:18}), ((2, 6, 2, 10), None), ((1, 2, 3, 10), {weight:10})]
        >>> G.edges(u=1, begin=5, end=9, data="weight")
        [((1, 2, 3, 10), 10)]
        """
        # If non of the nodes are defined the interval tree is queried for the list of edges,
        # otherwise the edges are returned based on the nodes in the self._adj.

        if not u and not v:
            if not begin and not end:
                iedges = self.tree[None:None]
            # interval filtering
            else:
                if begin and end and begin > end:
                    raise NetworkXError("IntervalGraph: interval end must be bigger than or equal to begin: "
                                        "begin: {}, end: {}.".format(begin, end))
                iedges = self.tree[begin:end]

        else:
            # Node filtering
            if u and v:
                if u not in self._adj:
                    return []
                if v not in self._adj:
                    return []

                iedges = [iv for iv in self._adj[u].keys() if iv[1] == v]
            elif u is not None:
                if u not in self._adj:
                    return []
                iedges = self._adj[u].keys()
            else:
                if v not in self._adj:
                    return []
                iedges = self._adj[v].keys()

            # Interval filtering
            if begin and end and begin > end:
                raise NetworkXError("IntervalGraph: interval end must be bigger than or equal to begin: "
                                    "begin: {}, end: {}.".format(begin, end))
            iedges = [iv for iv in iedges if IntervalGraph.__overlaps_or_contains(iv, begin, end)]

        # Appending attribute data if needed
        if data is False:
            return iedges if isinstance(iedges, list) else list(iedges)

        if data is True:
            return [(iv, self._adj[iv[0]][iv]) for iv in iedges]

        return [(iv, self._adj[iv[0]][iv][data]) if data in self._adj[iv[0]][iv].keys() else
                (iv, default) for iv in iedges]

    def remove_edge(self, u, v, begin=None, end=None, overlapping=True):
        """Remove the edge between u and v in the interval graph,
        during the given interval.

        Quiet if the specified edge is not present.

        Parameters
        ----------
        u, v : nodes
            Nodes can be, for example, strings or numbers.
            Nodes must be hashable (and not None) Python objects.
        begin : int or float, optional (default= beginning of the entire interval graph)
            Inclusive beginning time of the edge appearing in the interval graph.
        end : int or float, optional (default= end of the entire interval graph + 1)
            Non-inclusive ending time of the edge appearing in the interval graph.
            Must be bigger than or equal to begin.
            Note that the default value is shifted up by 1 to make it an inclusive end.
        overlapping : bool, optional (default= True)
            if True, remove the edge between u and v with overlapping interval
            with `begin` and `end`.
            if False, remove the edge between u and v with the exact interval.
            Note: if False, both `begin` and `end` must be defined, otherwise
            an exception is raised.

        Raises
        ------
        NetworkXError
            If `begin` and `end` are not defined and `overlapping= False`

        Examples
        --------
        >>> G = dnx.IntervalGraph()
        >>> G.add_edges_from([(1, 2, 3, 10), (2, 4, 1, 11), (6, 4, 5, 9), (1, 2, 8, 15)])
        >>> G.remove_edge(1, 2)
        >>> G.has_edge(1, 2)
        False

        With specific overlapping interval

        >>> G = dnx.IntervalGraph()
        >>> G.add_edges_from([(1, 2, 3, 10), (2, 4, 1, 11), (6, 4, 5, 9), (1, 2, 8, 15)])
        >>> G.remove_edge(1, 2, begin=2, end=4)
        >>> G.has_edge(1, 2, begin=2, end=4)
        False
        >>> G.has_edge(1, 2)
        True

        Exact interval match

        >>> G.remove_edge(2, 4, begin=1, end=11, overlapping=False)
        >>> G.has_edge(2, 4, begin=1, end=11)
        False
        """
        # remove edge between u and v with the exact given interval
        if not overlapping:
            if begin is None or end is None:
                raise NetworkXError("For exact interval match (overlapping=False), both begin and end must be defined.")

            iedge = self.edges(u, v, begin, end)
            if iedge is not None:
                self.__remove_iedge(iedge)
            return

        iedges_to_remove = []

        # remove every edge between u and v
        if begin is None and end is None:
            for iv in self._adj[u].keys():
                if iv[0] == v or iv[1] == v:
                    iedges_to_remove.append(iv)

        # remove edge between u and v with overlapping interval with the given interval
        if begin and end and begin > end:
            raise NetworkXError("IntervalGraph: interval end must be bigger than or equal to begin: "
                                "begin: {}, end: {}.".format(begin, end))

        for iv in self._adj[u].keys():
            if (iv[0] == v or iv[1] == v) and IntervalGraph.__overlaps_or_contains(iv, begin, end):
                iedges_to_remove.append(iv)

        # removing found iedges
        for iv in iedges_to_remove:
            self.__remove_iedge(iv)

    def degree(self, node=None, begin=None, end=None, delta=False):
        """Return the degree of a specified node between time begin and end.

        Parameters
        ----------
        node : Nodes can be, for example, strings or numbers, optional.
            Nodes must be hashable (and not None) Python objects.
        begin : int or float, optional (default= beginning of the entire interval graph)
            Inclusive beginning time of the edge appearing in the interval graph.
        end : int or float, optional (default= end of the entire interval graph)
            Non-inclusive ending time of the edge appearing in the interval graph.

        Returns
        -------
        Integer value of degree of specified node.
        If no node is specified, returns float mean degree value of graph.
        If delta is True, return list of tuples.
            First indicating the time a degree change occurred,
            Second indicating the degree after the change occured

        Examples
        --------
        >>> G = IntervalGraph()
        >>> G.add_edge(1, 2, 3, 5)
        >>> G.add_edge(2, 3, 8, 11)
        >>> G.degree(2)
        2
        >>> G.degree(2,2)
        2
        >>> G.degree(2,end=8)
        1
        >>> G.degree()
        1.33333
        >>> G.degree(2,delta=True)
        [(3, 1), (5, 0), (8, 1)]
        """

        # no specified node, return mean degree
        if node == None:
            n = 0
            l = 0
            for node in self.nodes(begin=begin, end=end):
                n += 1
                l += self.degree(node, begin=begin, end=end)
            return l / n

        # specified node, no degree_change, return degree
        if delta == False:
            return len(self.edges(u=node, begin=begin, end=end))

        # delta == True, return list of changes
        if begin == None:
            begin = self.tree.begin
        if end == None:
            end = self.tree.end

        current_degree = self.degree(node, begin=begin, end=begin)
        sd = SortedDict()
        output = []

        # for each edge determine if the begin and/or end value is in specified time period
        for edge in self.edges(u=node, begin=begin, end=end):
            if edge[2] >= begin:
                # if begin is in specified time period, add to SortedDict, with +1 to indicate begin
                sd.setdefault((edge[2], 1), []).append((edge[0], edge[1]))
            if edge[3] < end:
                # if begin is in specified time period, add to SortedDict, with -1 to indicate begin
                sd.setdefault((edge[3], -1), []).append((edge[0], edge[1]))

        for time in sd:
            for edge in sd[time]:
                # iterate through SortedDict, only advancing current degree if edge was not counted on init
                if time[0] != begin:
                    current_degree += time[1]
                output.append((time[0], current_degree))

        return output

    def __remove_iedge(self, iedge):
        """Remove the interval edge from the interval graph.

        Quiet if the specified edge is not present.

        Parameters
        ----------
        iedge : Interval object
            Interval edge to be removed.

        Examples
        --------
        >>> G = dnx.IntervalGraph()
        >>> G.add_edge(1, 2, 3, 10)
        >>> iedge = (1, 2, 3 4)
        >>> G.__remove_iedge(iedge)
        """
        self.tree.remove(iedge)
        self._adj[iedge[0]].pop(iedge, None)
        self._adj[iedge[1]].pop(iedge, None)

    @staticmethod
    def __overlaps_or_contains(iv, begin, end):
        """Returns True if interval `iv` overlaps with begin and end.

       Parameters
       ----------
       iv: Interval
       begin: int or float
            Inclusive beginning time of the node appearing in the interval graph.
        end: int or float
            Non-inclusive ending time of the node appearing in the interval graph.
            Must be bigger than or equal begin.
       """
        if not begin and not end:
            return True
        if not begin:
            return iv[2] < end
        if not end:
            return iv[3] > begin
        return (iv[2] < end and iv[3] > begin) or iv[2] == begin

    def to_networkx_graph(self, begin, end, multigraph=False, edge_data=False, edge_interval_data=False, node_data=False):
        """Return a networkx Graph or MultiGraph which includes all the nodes and
        edges which have overlapping intervals with the given interval.

        Wrapper function for IntervalGraph.to_subgraph. Refer to IntervalGraph.to_subgraph for full description.
        """
        return self.to_subgraph(begin=begin, end=end, multigraph=multigraph, edge_data=edge_data, edge_interval_data=edge_interval_data,
                                node_data=node_data)

    def to_subgraph(self, begin, end, multigraph=False, edge_data=False, edge_interval_data=False, node_data=False):
        """Return a networkx Graph or MultiGraph which includes all the nodes and
        edges which have overlapping intervals with the given interval.

        Parameters
        ----------
        begin: int or float
            Inclusive beginning time of the edge appearing in the interval graph.
        end: int or float
            Non-inclusive ending time of the edge appearing in the interval graph.
            Must be bigger than or equal to begin.
        multigraph: bool, optional (default= False)
            If True, a networkx MultiGraph will be returned. If False, networkx Graph.
        edge_data: bool, optional (default= False)
            If True, edges will keep their attributes.
        edge_interval_data: bool, optional (default= False)
            If True, each edge's attribute will also include its begin and end interval data.
            If `edge_data= True` and there already exist edge attributes with names begin and end,
            they will be overwritten.
        node_data : bool, optional (default= False)
            If True, each node's attributes will be included.

        See Also
        --------
        to_snapshots : divide the interval graph to snapshots

        Notes
        -----
        If multigraph= False, and edge_data=True or edge_interval_data=True,
        in case there are multiple edges, only one will show with one of the edge's attributes.

        Note: nodes with no edges will not appear in any subgraph.

        Examples
        --------
        >>> G = dnx.IntervalGraph()
        >>> G.add_edges_from([(1, 2, 3, 10), (2, 4, 1, 11), (6, 4, 12, 19), (2, 4, 8, 15)])
        >>> H = G.to_subgraph(4, 12)
        >>> type(H)
        <class 'networkx.classes.graph.Graph'>
        >>> list(H.edges(data=True))
        [(1, 2, {}), (2, 4, {})]

        >>> H = G.to_subgraph(4, 12, edge_interval_data=True)
        >>> type(H)
        <class 'networkx.classes.graph.Graph'>
        >>> list(H.edges(data=True))
        [(1, 2, {'end': 10, 'begin': 3}), (2, 4, {'end': 15, 'begin': 8})]

        >>> M = G.to_subgraph(4, 12, multigraph=True, edge_interval_data=True)
        >>> type(M)
        <class 'networkx.classes.multigraph.MultiGraph'>
        >>> list(M.edges(data=True))
        [(1, 2, {'end': 10, 'begin': 3}), (2, 4, {'end': 11, 'begin': 1}), (2, 4, {'end': 15, 'begin': 8})]
        """
        iedges = self.tree[begin:end]

        if multigraph:
            G = MultiGraph()
        else:
            G = Graph()

        if edge_data and edge_interval_data:
            G.add_edges_from((iedge[0], iedge[1],
                              dict(self._adj[iedge[0]][iedge], begin=iedge.begin, end=iedge.end))
                             for iedge in iedges)
        elif edge_data:
            G.add_edges_from((iedge[0], iedge[1], self._adj[iedge[0]][iedge].copy())
                             for iedge in iedges)
        elif edge_interval_data:
            G.add_edges_from((iedge[0], iedge[1], {'begin': iedge[2], 'end': iedge[3]})
                             for iedge in iedges)
        else:
            G.add_edges_from((iedge[0], iedge[1]) for iedge in iedges)

        # include node attributes
        if node_data:
            G.add_nodes_from((n, self._node[n].copy()) for n in G.nodes)

        return G

    def to_snapshots(self, number_of_snapshots=False, length_of_snapshots=False, multigraph=False, edge_data=False,
                     edge_interval_data=False,
                     node_data=False, return_length=False):
        """Return a list of networkx Graph or MultiGraph objects as snapshots
        of the interval graph in consecutive order.

        Parameters
        ----------
        number_of_snapshots : integer
            Number of snapshots to divide the interval graph into.
            Must be bigger than 2.
        length_of_snapshots : integer or float
            Length of snapshots to divide the interval graph into.
            Must be bigger than 1.
        multigraph : bool, optional (default= False)
            If True, a networkx MultiGraph will be returned. If False, networkx Graph.
        edge_data: bool, optional (default= False)
            If True, edges will keep their attributes.
        edge_interval_data : bool, optional (default= False)
            If True, each edge's attribute will also include its begin and end interval data.
            If `edge_data= True` and there already exist edge attributes with names begin and end,
            they will be overwritten.
        node_data : bool, optional (default= False)
            if True, each node's attributes will be included.
        return_length : bool, optional (default= False)
            If true, the length of snapshots will be returned as the second argument.

        See Also
        --------
        to_subgraph : subgraph based on an interval

        Notes
        -----
        In order to create snapshots, begin and end interval objects of the interval graph must be numbers.

        If multigraph= False, and edge_data=True or edge_interval_data=True,
        in case there are multiple edges, only one will show with one of the edge's attributes.

        Examples
        --------
        Snapshots of NetworkX Graph

        >>> G = dnx.IntervalGraph()
        >>> G.add_edges_from([(1, 2, 3, 10), (2, 4, 1, 11), (6, 4, 12, 19), (2, 4, 8, 15)])
        >>> S, l = G.to_snapshots(2, edge_interval_data=True, return_length=True)
        >>> S
        [<networkx.classes.graph.Graph object at 0x100000>, <networkx.classes.graph.Graph object at 0x150d00>]
        >>> l
        9.0
        >>> for g in S:
        >>> ... g.edges(data=True))
        [(1, 2, {'begin': 3, 'end': 10}), (2, 4, {'begin': 8, 'end': 15})]
        [(2, 4, {'begin': 8, 'end': 15}), (4, 6, {'begin': 12, 'end': 19})]

        Snapshots of NetworkX MultiGraph

        >>> S, l = G.to_snapshots(3, multigraph=True, edge_interval_data=True, return_length=True)
        >>> S
        [<networkx.classes.multigraph.MultiGraph object at 0x1060d40b8>, <networkx.classes.multigraph.MultiGraph object at 0x151020c9e8>, <networkx.classes.multigraph.MultiGraph object at 0x151021d390>]
        >>> l
        6.0
        >>> for g in S:
        >>> ... g.edges(data=True))
        [(1, 2, {'end': 10, 'begin': 3}), (2, 4, {'end': 11, 'begin': 1})]
        [(1, 2, {'end': 10, 'begin': 3}), (2, 4, {'end': 11, 'begin': 1}), (2, 4, {'end': 15, 'begin': 8}), (4, 6, {'end': 19, 'begin': 12})]
        [(2, 4, {'end': 15, 'begin': 8}), (4, 6, {'end': 19, 'begin': 12})]
        """

        if type(number_of_snapshots) is bool and type(length_of_snapshots) is bool:
            raise NetworkXError("IntervalGraph: either number of snapshots or length of snapshots must be given.")

        if type(number_of_snapshots) is not bool and type(length_of_snapshots) is not bool:
            raise NetworkXError("IntervalGraph: either number of snapshots or length of snapshots must be given, "
                                "not both.")

        begin, end = self.interval()
        if type(length_of_snapshots) is int or type(length_of_snapshots) is float:
            if length_of_snapshots < 0:
                raise NetworkXError("IntervalGraph: length of snapshots must be bigger than 0. "
                                    "{0} was passed.".format(number_of_snapshots))
            number_of_snapshots = (end - begin) // length_of_snapshots
            if (end - begin) % length_of_snapshots != 0:
                number_of_snapshots += 1

        if number_of_snapshots < 2 or type(number_of_snapshots) is not int:
            raise NetworkXError("IntervalGraph: number of snapshots must be an integer and 2 or bigger. "
                                "{0} was passed.".format(number_of_snapshots))

        if length_of_snapshots is False:
            length_of_snapshots = (end - begin) / number_of_snapshots

        snapshots = []
        end_inclusive_addition = 0
        for i in range(number_of_snapshots):
            # since to_subgraph is end non-inclusive, shift the end up by 1 to include end in the last snapshot.
            if i == number_of_snapshots - 1:
                end_inclusive_addition = 1

            snapshots.append(
                self.to_subgraph(begin + length_of_snapshots * i,
                                 begin + length_of_snapshots * (i + 1) + end_inclusive_addition,
                                 multigraph=multigraph, edge_data=edge_data, edge_interval_data=edge_interval_data,
                                 node_data=node_data))
        if return_length:
            return snapshots, length_of_snapshots

        return snapshots

    def to_snapshot_graph(self, number_of_snapshots=False, length_of_snapshots=False, multigraph=False, edge_data=False,
                          edge_timestamp_data=False,
                          node_data=False, return_length=False):
        """
        Return a dnx.SnapshotGraph of the interval graph.

        Parameters
        ----------
        number_of_snapshots : integer
            Number of snapshots to divide the interval graph into.
            Must be bigger than 2.
        length_of_snapshots : integer or float
            Length of snapshots to divide the interval graph into.
            Must be bigger than 1.
        multigraph : bool, optional (default= False)
            If True, a networkx MultiGraph will be returned. If False, networkx Graph.
        edge_data: bool, optional (default= False)
            If True, edges will keep their attributes.
        edge_timestamp_data : bool, optional (default= False)
            If True, each edge's attribute will also include its timestamp data.
            If `edge_data= True` and there already exist edge attributes named timestamp
            it will be overwritten.
        node_data : bool, optional (default= False)
            if True, each node's attributes will be included.
        return_length : bool, optional (default= False)
            If true, the length of snapshots will be returned as the second argument.

        See Also
        --------
        to_snapshots : divide the interval graph to snapshots

        Notes
        -----
        In order to create snapshots, timestamps of edges of the interval graph must be numbers.

        If multigraph= False, and edge_data=True or edge_timestamp_data=True,
        in case there are multiple edges, only one will show with one of the edge's attributes.

        Examples
        --------
        Snapshots of NetworkX Graph

        >>> G = dnx.IntervalGraph()
        >>> G.add_edges_from([(1, 2, 10, 11), (2, 4, 11, 12), (6, 4, 19, 20), (2, 4, 15, 16)])
        >>> S, l = G.to_snapshot_graph(2, edge_timestamp_data=True, return_length=True)
        >>> for g in S:
        >>> ... g.edges(data=True))
        [(1, 2, {'start_time': 10, 'end_time': 11}), (2, 4, {'start_time': 11, 'end_time': 12})]
        [(2, 4, {'start_time': 15, 'end_time': 16}), (4, 6, {'start_time': 19, 'end_time': 20})]

        Snapshots of NetworkX MultiGraph

        >>> S, l = G.to_snapshot_graph(3, multigraph=True, edge_timestamp_data=True, return_length=True)
        >>> for g in S:
        >>> ... g.edges(data=True))
        [(1, 2, {'start_time': 10, 'end_time': 11}), (2, 4, {'start_time': 11, 'end_time': 12})]
        [(2, 4, {'start_time': 15, 'end_time': 16})]
        [(4, 6, {'start_time': 19, 'end_time': 20})]
        """

        G = dnx.SnapshotGraph()

        if return_length == True:
            snapshots, l = self.to_snapshots(number_of_snapshots=number_of_snapshots,
                                             length_of_snapshots=length_of_snapshots,
                                             multigraph=multigraph, edge_data=edge_data,
                                             edge_timestamp_data=edge_timestamp_data,
                                             node_data=node_data, return_length=return_length)
            for snapshot in snapshots:
                G.insert(snapshot)

            return G, l

        else:
            snapshots = self.to_snapshots(number_of_snapshots=number_of_snapshots,
                                          length_of_snapshots=length_of_snapshots,
                                          multigraph=multigraph, edge_data=edge_data,
                                          edge_timestamp_data=edge_timestamp_data,
                                          node_data=node_data, return_length=return_length)
            for snapshot in snapshots:
                G.insert(snapshot)

            return G

    @staticmethod
    def from_snapshot_graph(snapshot_graph, begin=0, period=1):
        """Convert a SnapshotGraph to a IntervalGraph.

        Parameters
        ----------
        snapshot_graph : SnapshotGraph

        begin : integer or double
            Timestamp of first snapshot.

        period : integer or double
            Time between each successive snapshot.

        Returns
        -------
        G: IntervalGraph
            The graph corresponding to the lines in edge list.

        Examples
        --------
        >>> sg = SnapshotGraph()
        >>> sg.add_snapshot([(1, 2), (1, 3)])
        >>> sg.add_snapshot([(1, 4), (1, 3)])
        >>> sg.add_edges_from([(5, 6), (7, 6)], [0])
        >>> sg.add_edges_from([(8, 9), (10, 11)], [0, 1])
        >>> sg.add_edges_from([(8,9)],weight=1)
        >>> ig = IntervalGraph.from_snapshot_graph(sg,0,1)
        """
        G = IntervalGraph()
        edge_dict = {}

        for snapshot in snapshot_graph.get():
            for edge in snapshot.edges(data=True):
                u_v = (edge[0], edge[1])
                if u_v in edge_dict:
                    if begin in edge_dict[u_v]:
                        edge_dict[u_v][begin + period] = edge_dict[u_v][begin]
                        del edge_dict[u_v][begin]
                    else:
                        edge_dict[u_v][begin + period] = (begin, edge[2])
                else:
                    edge_dict[u_v] = {begin + period: (begin, edge[2])}

            begin += period

        for edge_list in edge_dict:
            for edge in edge_dict[edge_list]:
                G.add_edge(edge_list[0], edge_list[1], edge_dict[edge_list][edge][0], edge,
                           **edge_dict[edge_list][edge][1])

        return G

    @staticmethod
    def from_networkx_graph(graph, begin='begin', end='end'):
        """Convert a NetworkX Graph to a IntervalGraph.

        Parameters
        ----------
        graph : NetworkX Graph

        begin : string
            Attribute for beginning timestamp in NetworkX Graph.

        end : string
            Attribute for ending timestamp in NetworkX Graph.

        Returns
        -------
        G: IntervalGraph
            The graph corresponding to the lines in edge list.

        Examples
        --------

        graph = nx.Graph()
        graph.add_edge(1,2,begin=10,end=11,weight=1.5)
        graph.add_edge(2,3,begin=11,end=13)

        ig = IntervalGraph.from_networkx_graph(graph)
      """

        G = IntervalGraph()

        for edge in graph.edges(data=True):
            attr = {}

            for key in edge[2]:
                if key != begin and key != end:
                    attr[key] = edge[2][key]

            G.add_edge(edge[0], edge[1], edge[2][begin], edge[2][end], **attr)

        return G

    @staticmethod
    def load_from_txt(path, delimiter=" ", nodetype=int, intervaltype=float, order=('u', 'v', 'begin', 'end'),
                      merge=(False, 0), comments="#"):
        """Read interval graph in from path.
           Both interval times must be integers or floats.
           Nodes can be any hashable objects.
           Edge Attributes can be assigned with in the following format: Key=Value

        Parameters
        ----------
        path : string or file
           Filename to read.

        nodetype : Python type, optional (default= int)
           Convert nodes to this type.

        intervaltype : Python type, optional (default= float)
        Convert interval begin and end to this type.
        This must be an orderable type, ideally int or float. Other orderable types have not been fully tested.

        order : Python 4-tuple, optional (default= ('u', 'v', 'begin', 'end'))
        This may be a 4-tuple containing strings 'u', 'v', 'begin', and 'end'. 'u' specifies the starting node,
        'v' the ending node, 'begin' the interval start time, and 'end' the interval end time.
        This may be a 4-tuple containing strings 'u', 'v', 'begin' or 'end', and duration.
        Duration must be positive number greater than or equal to 1, must be in last position of tuple.

        merge : 2-tuple, optional (default= (False, 0))
        Attempt to merge discrete edge timestamps into continuous edges with specified grace period.
        Note: grace period is offset by +-1 to provide inclusive ends. See IntervalGraph.edges for more information.

        comments : string, optional
           Marker for comment lines

        delimiter : string, optional
           Separator for node labels.  The default is whitespace. Cannot be =.

        Returns
        -------
        G: IntervalGraph
            The graph corresponding to the lines in edge list.

        Examples
        --------
        >>> G=dnx.IntervalGraph.load_from_txt("my_dygraph.txt")

        The optional nodetype is a function to convert node strings to nodetype.

        For example

        >>> G=dnx.IntervalGraph.load_from_txt("my_dygraph.txt", nodetype=float)

        will attempt to convert all nodes to float type.

        Since nodes must be hashable, the function nodetype must return hashable
        types (e.g. int, float, str, frozenset - or tuples of those, etc.)
        """

        ig = IntervalGraph()

        if delimiter == '=':
            raise ValueError("Delimiter cannot be =.")

        if len(order) != 4 or 'u' not in order or 'v' not in order or ('begin' not in order and 'end' not in order):
            raise ValueError("Order must be a 4-tuple containing strings 'u', 'v', 'begin', and 'end' OR 'u', 'v', "
                             "'begin' or 'end', and duration.")

        with open(path, 'r') as file:
            for line in file:
                p = line.find(comments)
                if p >= 0:
                    line = line[:p]
                if not len(line):
                    continue

                line = line.rstrip().split(delimiter)
                u = line[order.index('u')]
                v = line[order.index('v')]
                if 'begin' in order and 'end' in order:
                    begin = line[order.index('begin')]
                    end = line[order.index('end')]
                elif 'begin' in order:
                    begin = intervaltype(line[order.index('begin')])
                    end = begin + order[3]
                elif 'end' in order:
                    end = intervaltype(line[order.index('end')])
                    begin = end - order[3]

                edgedata = {}
                try:
                    for data in line[4:]:
                        key, value = data.split('=')
                        try:
                            value = float(value)
                        except:
                            pass
                        edgedata[key] = value
                except:
                    pass

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
                    begin = intervaltype(begin)
                    end = intervaltype(end)
                except:
                    raise TypeError("Failed to convert interval time to {}".format(intervaltype))

                if merge[0]:
                    for edge, edge_data in ig.edges(u, v, begin - merge[1] - 1, end + merge[1] + 1, data=True):
                        if edge_data != edgedata:
                            ig.add_edge(u, v, begin, end ** edgedata)
                        else:
                            begin = min(begin, edge[0])
                            end = max(end, edge[1])
                            ig.remove_edge(u, v, edge[0], edge[1])
                            ig.add_edge(u, v, begin, end, **edgedata)

                ig.add_edge(u, v, begin, end, **edgedata)

        return ig

    def save_to_txt(self, path, delimiter=" "):
        """Write interval graph to path.
           Every line in the file must be an edge in the following format: "node node begin end".
           Begin, end must be integers or floats.
           Nodes can be any hashable objects.

        Parameters
        ----------
        path : string or file
           Filename to read.

        delimiter : string, optional
           Separator for node labels.  The default is whitespace. Cannot be =.

        Examples
        --------
        >>> G.save_to_txt("my_dygraph.txt")
        """
        if len(self) == 0:
            raise ValueError("Given graph is empty.")

        if delimiter == '=':
            raise ValueError("Delimiter cannot be =.")

        with open(path, 'w') as file:
            for edge in self.edges(data=True):
                line = str(edge[0][0]) + delimiter + str(edge[0][1]) + delimiter + str(edge[0][2]) + delimiter + str(edge[0][3])
                for key in edge[1]:
                    line += delimiter + str(key) + '=' + str(edge[1][key])
                line += '\n'

                file.write(line)
