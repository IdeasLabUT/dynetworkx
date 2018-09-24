import dynetworkx as dnx
from networkx.classes.graph import Graph
from networkx.exception import NetworkXError
from intervaltree import Interval, IntervalTree
from networkx.classes.multigraph import MultiGraph
from networkx.classes.reportviews import NodeView, EdgeView, NodeDataView


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
    which makes interval graph analyes possible.

    The Graph class uses a dict-of-dict-of-dict data structure.
    The outer dict (node_dict) holds adjacency information keyed by node.
    The next dict (adjlist_dict) represents the adjacency information and holds
    edge data keyed by interval object.  The inner dict (edge_attr_dict) represents
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
        self._adj = {}
        self._node = {}

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
        return self.tree.begin(), self.tree.end()

    def add_node(self, node_for_adding, **attr):
        """Add a single node `node_for_adding`  and update node attributes.

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
        if node_for_adding not in self._node:
            self._adj[node_for_adding] = {}
            self._node[node_for_adding] = attr
        else:  # update attr even if node already exists
            self._node[node_for_adding].update(attr)

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

    def number_of_nodes(self, begin=None, end=None):
        """Return the number of nodes in the interval graph between the given interval.

        Parameters
        ----------
        begin: integer, optional  (default= beginning of the entire interval graph)
            Inclusive beginning time of the node appearing in the interval graph.
        end: integer, optional  (default= end of the entire interval graph + 1)
            Non-inclusive ending time of the node appearing in the interval graph.
            Must be bigger than begin.
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

        if begin is None:
            begin = self.tree.begin()

        if end is None:
            end = self.tree.end() + 1

        iedges = self.tree[begin:end]

        inodes = set()

        for iv in iedges:
            inodes.add(iv.data[0])
            inodes.add(iv.data[1])

        return len(inodes)

    def has_node(self, n, begin=None, end=None):
        """Return True if the interval graph contains the node n, during the given interval.

        Identical to `n in G` when 'begin' and 'end' are not defined.

        Parameters
        ----------
        n : node
        begin: integer, optional  (default= beginning of the entire interval graph)
            Inclusive beginning time of the node appearing in the interval graph.
        end: integer, optional  (default= end of the entire interval graph + 1)
            Non-inclusive ending time of the node appearing in the interval graph.
            Must be bigger than begin.
            Note that the default value is shifted up by 1 to make it an inclusive end.

        Examples
        --------
        >>> G = dnx.IntervalGraph()
        >>> G.add_ndoe(1)
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
        try:
            exists_node = n in self._node
        except TypeError:
            exists_node = False

        if (begin is None and end is None) or not exists_node:
            return exists_node

        if begin is None:
            begin = self.tree.begin()

        if end is None:
            end = self.tree.end() + 1

        iedges = self._adj[n].keys()

        for iv in iedges:
            if iv.overlaps(begin=begin, end=end):
                return True

        return False

    def nodes(self, begin=None, end=None, data=False, default=None):
        """A NodeDataView of the IntervalGraph nodes.

        A nodes is considered to be present during an interval, if it has
        an edge with overlapping interval.

        Parameters
        ----------
        begin: integer, optional  (default= beginning of the entire interval graph)
            Inclusive beginning time of the node appearing in the interval graph.
        end: integer, optional  (default= end of the entire interval graph + 1)
            Non-inclusive ending time of the node appearing in the interval graph.
            Must be bigger than begin.
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

        if begin is None:
            begin = self.tree.begin()

        if end is None:
            end = self.tree.end() + 1

        iedges = self.tree[begin:end]

        inodes = set()
        for iv in iedges:
            inodes.add(iv.data[0])
            inodes.add(iv.data[1])

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
        begin: integer, optional  (default= beginning of the entire interval graph)
            Inclusive beginning time of the node appearing in the interval graph.
        end: integer, optional  (default= end of the entire interval graph + 1)
            Non-inclusive ending time of the node appearing in the interval graph.
            Must be bigger than begin.
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
            if begin is None:
                begin = self.tree.begin()

            if end is None:
                end = self.tree.end() + 1

            for iedge in self.tree[begin:end]:
                if iedge.data[0] == n or iedge.data[1] == n:
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

        iedge = self.__get_iedge_in_tree(begin, end, u, v)

        # if edge exists, just update attr
        if iedge is not None:
            # since both point to the same attr, updating one is enough
            self._adj[u][iedge].update(attr)
            return

        iedge = Interval(begin, end, (u, v))

        # add nodes
        if u not in self._node:
            self._adj[u] = {}
            self._node[u] = {}
        if v not in self._node:
            self._adj[v] = {}
            self._node[v] = {}

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
        begin : integer, optional (default= beginning of the entire interval graph)
            Inclusive beginning time of the node appearing in the interval graph.
        end : integer, optional (default= end of the entire interval graph + 1)
            Non-inclusive ending time of the node appearing in the interval graph.
            Must be bigger than begin.
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

        With specific overlapping interval
        >>> G.has_edge(1, 2, begin=2)
        True
        >>> G.has_edge(2, 4, begin=12)
        False

        Exact interval match
        >>> G.has_edge(2, 4, begin=1, end=11)
        True
        >>> G.has_edge(2, 4, begin=2, end=11)
        False
        """

        if begin is None and end is None:
            for iv in self._adj[u].keys():
                if iv.data[0] == v or iv.data[1] == v:
                    return True
            return False

        if not overlapping:
            if begin is None or end is None:
                raise NetworkXError("For exact interval match (overlapping=False), both begin and end must be defined.")

            return self.__get_iedge_in_tree(u, v, begin, end) is not None

        if begin is None:
            begin = self.tree.begin()

        if end is None:
            end = self.tree.end() + 1

        for iv in self._adj[u].keys():
            if (iv.data[0] == v or iv.data[1] == v) and iv.overlaps(begin=begin, end=end):
                return True
        return False

    def edges(self, u=None, v=None, begin=None, end=None, data=False, default=None):
        """A list of Interval objects of the IntervalGraph edges.

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
        begin: integer, optional  (default= beginning of the entire interval graph)
            Inclusive beginning time of the edge appearing in the interval graph.
        end: integer, optional  (default= end of the entire interval graph + 1)
            Non-inclusive ending time of the edge appearing in the interval graph.
            Must be bigger than begin.
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
        [Interval(8, 15, (2, 4)), Interval(3, 10, (1, 2)), Interval(1, 11, (2, 4)), Interval(12, 19, (6, 4))]

        To get edges which appear in a specific interval:
        >>> G.edges(begin=10)
        [Interval(12, 19, (6, 4)), Interval(1, 11, (2, 4)), Interval(8, 15, (2, 4))]
        >>> G.edges(end=5)
        [Interval(3, 10, (1, 2)), Interval(1, 11, (2, 4))]
        >>> G.edges(begin=2, end=4)
        [Interval(3, 10, (1, 2)), Interval(1, 11, (2, 4))]

        To get edges with either of the two nodes being defined:
        >>> G.edges(u=2)
        [Interval(3, 10, (1, 2)), Interval(1, 11, (2, 4)), Interval(8, 15, (2, 4))]
        >>> G.edges(u=2, begin=11)
        [Interval(1, 11, (2, 4)), Interval(8, 15, (2, 4))]
        >>> G.edges(u=2, v=4, end=8)
        [Interval(1, 11, (2, 4))]
        >>> G.edges(u=1, v=6)
        []

        To get a list of edges with data:
        >>> G = dnx.IntervalGraph()
        >>> G.add_edge(1, 3, 1, 4, weight=8, height=18)
        >>> G.add_edge(1, 2, 3, 10, weight=10)
        >>> G.add_edge(2, 6, 2, 10)
        >>> G.edges(data="weight")
        [(Interval(2, 8, (2, 3)), None), (Interval(3, 10, (1, 2)), 10), (Interval(1, 4, (1, 3)), 8)]
        >>> G.edges(data="weight", default=5)
        [(Interval(2, 8, (2, 3)), 5), (Interval(3, 10, (1, 2)), 10), (Interval(1, 4, (1, 3)), 8)]
        >>> G.edges(data=True)
        [(Interval(2, 8, (2, 3)), {}), (Interval(3, 10, (1, 2)), {'weight': 10}), (Interval(1, 4, (1, 3)), {'height': 18, 'weight': 8})]
        >>> G.edges(u=1, begin=5, end=9, data="weight")
        [(Interval(3, 10, (1, 2)), 10)]
        """

        # If non of the nodes are defined the interval tree is queried for the list of edges,
        # otherwise the edges are returned based on the nodes in the self._adj.o
        if u is None and v is None:
            if begin is None and end is None:
                iedges = self.tree.all_intervals
            # interval filtering
            else:
                if begin is None:
                    begin = self.tree.begin()
                if end is None:
                    end = self.tree.end() + 1

                iedges = self.tree[begin:end]

        else:
            # Node filtering
            if u is not None and v is not None:
               iedges = [iv for iv in self._adj[u].keys() if iv.data[0] == v or iv.data[1] == v]
            elif u is not None:
                iedges = self._adj[u].keys()
            else:
                iedges = self._adj[v].keys()

            # Interval filtering
            if begin is not None and end is not None:
                iedges = [iv for iv in iedges if iv.end >= begin and iv.begin < end]
            elif begin is not None:
                iedges = [iv for iv in iedges if iv.end >= begin]
            elif end is not None:
                iedges = [iv for iv in iedges if iv.begin < end]

        # Appending attribute data if needed
        if data is False:
            return iedges if isinstance(iedges, list) else list(iedges)

        if data is True:
            return [(iv, self._adj[iv.data[0]][iv]) for iv in iedges]

        return [(iv, self._adj[iv.data[0]][iv][data]) if data in self._adj[iv.data[0]][iv].keys() else
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
        begin : integer, optional (default= beginning of the entire interval graph)
            Inclusive beginning time of the edge appearing in the interval graph.
        end : integer, optional (default= end of the entire interval graph + 1)
            Non-inclusive ending time of the edge appearing in the interval graph.
            Must be bigger than begin.
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

            iedge = self.__get_iedge_in_tree(u, v, begin, end)
            if iedge is None:
                return
            self.__remove_iedge(iedge)
            return

        iedges_to_remove = []

        # remove every edge between u and v
        if begin is None and end is None:
            for iv in self._adj[u].keys():
                if iv.data[0] == v or iv.data[1] == v:
                    iedges_to_remove.append(iv)

        # remove edge between u and v with overlapping interval with the given interval
        if begin is None:
            begin = self.tree.begin()

        if end is None:
            end = self.tree.end() + 1

        for iv in self._adj[u].keys():
            if (iv.data[0] == v or iv.data[1] == v) and iv.overlaps(begin=begin, end=end):
                iedges_to_remove.append(iv)

        # removing found iedges
        for iv in iedges_to_remove:
            self.__remove_iedge(iv)

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
        >>> iedge = Interval(3, 10, (1, 2))   # Interval(begin, end, (u, v))
        >>> G.__remove_iedge(iedge)
        """
        self.tree.discard(iedge)
        self._adj[iedge.data[0]].pop(iedge, None)
        self._adj[iedge.data[1]].pop(iedge, None)

    def __get_iedge_in_tree(self, u, v, begin, end):
        """Return interval edge if found in the interval graph with the exact interval,
        otherwise return None.

        Parameters
        ----------
        u, v : nodes
            Nodes can be, for example, strings or numbers.
            Nodes must be hashable (and not None) Python objects.
        begin : integer
            Inclusive beginning time of the edge appearing in the interval graph.
        end : integer
            Non-inclusive ending time of the edge appearing in the interval graph.
            Must be bigger than begin.

        Examples
        --------
        >>> G = dnx.IntervalGraph()
        >>> G.add_edge(1, 2, 3, 10)
        >>> G.__get_iedge_in_tree(2, 1, 3, 10)
        Interval(3, 10, (1, 2))
        >>> G.__get_iedge_in_tree(2, 1, 4, 10)
        None
        """

        temp_iedge = Interval(begin, end, (u, v))
        if temp_iedge in self.tree:
            return temp_iedge

        temp_iedge = Interval(begin, end, (v, u))
        if temp_iedge in self.tree:
            return temp_iedge

        return None

    def to_subgraph(self, begin, end, multigraph=False, edge_data=False, edge_interval_data=False, node_data=False):
        """Return a networkx Graph or MultiGraph which includes all the nodes and
        edges which have overlapping intervals with the given interval.

        Parameters
        ----------
        begin: integer
            Inclusive beginning time of the edge appearing in the interval graph.
            Must be bigger than begin.
        end: integer
            Non-inclusive ending time of the edge appearing in the interval graph.
        multigraph: bool, optional (default= False)
            If True, a networkx MultiGraph will be returned. If False, networkx Graph.
        edge_data: bool, optional (default= False)
            If True, edges will keep their attributes.
        edge_interval_data: bool, optional (default= False)
            If True, each edge's attribute will also include its begin and end interval data.
            If `edge_data= True` and there already exist edge attributes with names begin and end,
            they will be overwritten.
        node_data : bool, optional (default= False)
            if True, each node's attributes will be included.

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

        if end <= begin:
            raise NetworkXError("IntervalGraph: subgraph duration must be strictly bigger than zero: "
                                "begin: {}, end: {}.".format(begin, end))

        iedges = self.tree[begin:end]

        if multigraph:
            G = MultiGraph()
        else:
            G = Graph()

        if edge_data and edge_interval_data:
            G.add_edges_from((iedge.data[0], iedge.data[1],
                              dict(self._adj[iedge.data[0]][iedge], begin=iedge.begin, end=iedge.end))
                             for iedge in iedges)
        elif edge_data:
            G.add_edges_from((iedge.data[0], iedge.data[1], self._adj[iedge.data[0]][iedge].copy())
                             for iedge in iedges)
        elif edge_interval_data:
            G.add_edges_from((iedge.data[0], iedge.data[1], {'begin': iedge.begin, 'end': iedge.end})
                             for iedge in iedges)
        else:
            G.add_edges_from((iedge.data[0], iedge.data[1]) for iedge in iedges)

        # include node attributes
        if node_data:
            G.add_nodes_from((n, self._node[n].copy()) for n in G.nodes)

        return G

    def to_snapshots(self, number_of_snapshots, multigraph=False, edge_data=False, edge_interval_data=False,
                     node_data=False, return_length=False):
        """Return a list of networkx Graph or MultiGraph objects as snapshots
        of the interval graph in consecutive order.

        Parameters
        ----------
        number_of_snapshots : integer
            Number of snapshots to divide the interval graph into.
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

        if number_of_snapshots < 2 or type(number_of_snapshots) is not int:
            raise NetworkXError("IntervalGraph: number of snapshots must be an integer and 2 or bigger. "
                                "{0} was passed.".format(number_of_snapshots))

        begin, end = self.interval()
        snapshot_len = (end - begin) / number_of_snapshots

        snapshots = []
        end_inclusive_addition = 0
        for i in range(number_of_snapshots):
            # since to_subgraph is end non-inclusive, shift the end up by 1 to include end in the last snapshot.
            if i == number_of_snapshots - 1:
                end_inclusive_addition = 1

            snapshots.append(
                self.to_subgraph(begin + snapshot_len * i, begin + snapshot_len * (i + 1) + end_inclusive_addition,
                                 multigraph=multigraph, edge_data=edge_data, edge_interval_data=edge_interval_data,
                                 node_data=node_data))
        if return_length:
            return snapshots, snapshot_len

        return snapshots

    @staticmethod
    def load_from_txt(path, delimiter=" ", nodetype=None, comments="#"):
        """Read interval graph in from path.
           Every line in the file must be an edge in the following format: "node node begin end".
           Both interval times must be integers. Nodes can be any hashable objects.

        Parameters
        ----------
        path : string or file
           Filename to read.

        nodetype : Python type, optional
           Convert nodes to this type.

        comments : string, optional
           Marker for comment lines

        delimiter : string, optional
           Separator for node labels.  The default is whitespace.

        Returns
        -------
        G: IntervalGraph
            The graph corresponding to the lines in edge list.

        Examples
        --------
        >>> G=dnx.IntervalGraph.load_from_txt("my_dygraph.txt")

        The optional nodetype is a function to convert node strings to nodetype.

        For example

        >>> G=dnx.IntervalGraph.load_from_txt("my_dygraph.txt", nodetype=int)

        will attempt to convert all nodes to integer type.

        Since nodes must be hashable, the function nodetype must return hashable
        types (e.g. int, float, str, frozenset - or tuples of those, etc.)
        """

        ig = IntervalGraph()

        with open(path, 'r') as file:
            for line in file:
                p = line.find(comments)
                if p >= 0:
                    line = line[:p]
                if not len(line):
                    continue

                line = line.rstrip().split(delimiter)
                u, v, begin, end = line

                if nodetype is not None:
                    try:
                        u = nodetype(u)
                        v = nodetype(v)
                    except:
                        raise TypeError("Failed to convert node to type {0}".format(nodetype))

                try:
                    begin = int(begin)
                    end = nodetype(end)
                except:
                    raise TypeError("Failed to convert time to type int")

                ig.add_edge(u, v, begin, end)

        return ig
