import dynetworkx as dnx
from networkx.classes.graph import Graph
from networkx.exception import NetworkXError
from networkx.classes.multigraph import MultiGraph
from networkx.classes.reportviews import NodeDataView
from sortedcontainers import SortedDict
import random
import math
from timeit import default_timer as timer
from sklearn.linear_model import LinearRegression
from itertools import product


class ImpulseGraph(object):
    """Base class for undirected impulse graphs.

    The ImpulseGraph class allows any hashable object as a node
    and can associate key/value attribute pairs with each undirected edge.

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

    >>> G = dnx.ImpulseGraph()

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

    >>> G = dnx.ImpulseGraph(day="Friday")
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
        >>> G = dnx.ImpulseGraph()
        >>> G = dnx.ImpulseGraph(name='my graph')
        >>> G.graph
        {'name': 'my graph'}
        """

        self.tree = SortedDict()
        self.graph = {}  # dictionary for graph attributes
        self._node = {}
        self._adj = {}
        self._model = None

        self.graph.update(attr)

    @property
    def name(self):
        """String identifier of the impulse graph.

        This impulse graph attribute appears in the attribute dict IG.graph
        keyed by the string `"name"`. as well as an attribute (technically
        a property) `IG.name`. This is entirely user controlled.
        """
        return self.graph.get('name', '')

    @name.setter
    def name(self, s):
        self.graph['name'] = s

    def __str__(self):
        """Return the impulse graph name.

        Returns
        -------
        name : string
            The name of the impulse graph.

        Examples
        --------
        >>> G = dnx.ImpulseGraph(name='foo')
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
        >>> G = dnx.ImpulseGraph()
        >>> G.add_nodes_from([2, 4, 5])
        >>> len(G)
        3

        """

        return len(self._node)

    def __contains__(self, n):
        """Return True if n is a node, False otherwise. Use: 'n in G'.

        Examples
        --------
        >>> G = dnx.ImpulseGraph()
        >>> G.add_node(2)
        >>> 2 in G
        True
        """

        return n in self._node

    def interval(self):
        """Return a 2-tuple as (begin, end) interval of the entire
         impulse graph.

        Examples
        --------
        >>> G = dnx.ImpulseGraph()
        >>> G.add_edges_from([(1, 2, 10), (3, 7, 16)])
        >>> G.interval()
        (10, 16)
        """
        if len(self.tree.keys()) == 0:
            raise IndexError("ImpulseGraph is empty.")
        return list(self.tree.keys())[0], list(self.tree.keys())[-1]

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
        >>> G = dnx.ImpulseGraph()
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
        >>> G = dnx.ImpulseGraph()
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

    def number_of_nodes(self, begin=None, end=None, inclusive=(True, False)):
        """Return the number of nodes in the impulse graph between the given interval.

        Parameters
        ----------
        begin: int or float, optional (default= beginning of the entire impulse graph)
        end: int or float, optional  (default= end of the entire impulse graph)
            Must be bigger than or equal begin.
        inclusive: 2-tuple boolean that determines inclusivity of begin and end

        Returns
        -------
        nnodes : int
            The number of nodes in the impulse graph.

        See Also
        --------
        __len__

        Examples
        --------
        >>> G = dnx.ImpulseGraph()
        >>> G.add_edges_from([(1, 2, 5), (3, 4, 11)])
        >>> len(G)
        4
        >>> G.number_of_nodes()
        4
        >>> G.number_of_nodes(begin=6)
        2
        >>> G.number_of_nodes(begin=5, end=8)
        2
        >>> G.number_of_nodes(end=11)
        2
        """

        if begin is None and end is None:
            return len(self._node)
        if end is None:
            inclusive = (inclusive[0], True)

        inodes = set()
        for edge in self.__search_tree(begin, end, inclusive=inclusive):
            inodes.add(edge[0])
            inodes.add(edge[1])

        return len(inodes)

    def has_node(self, n, begin=None, end=None, inclusive=(True, False)):
        """Return True if the impulse graph contains the node n, during the given interval.

        Identical to `n in G` when 'begin' and 'end' are not defined.

        Parameters
        ----------
        n : node
        begin: int or float, optional  (default= beginning of the entire impulse graph)
        end: int or float, optional  (default= end of the entire impulse graph)
            Must be bigger than or equal begin.
        inclusive: 2-tuple boolean that determines inclusivity of begin and end

        Examples
        --------
        >>> G = dnx.ImpulseGraph()
        >>> G.add_node(1)
        >>> G.has_node(1)
        True

        It is more readable and simpler to use

        >>> 1 in G
        True

        With interval query:

        >>> G.add_edge(3, 4, 5)
        >>> G.has_node(3)
        True
        >>> G.has_node(3, begin=2)
        True
        >>> G.has_node(3, end=2)
        False
        """

        if n not in self._node:
            return False

        if begin is None and end is None:
            return True

        begin, end = self.__validate_interval(begin, end)

        for edge in self.__search_tree(begin, end, inclusive=inclusive):
            if n == edge[0] or n == edge[1]:
                return True
        return False

    def nodes(self, begin=None, end=None, inclusive=(True, False), data=False, default=None):
        """A NodeDataView of the ImpulseGraph nodes.

        A nodes is considered to be present during an interval, if it has
        an edge with overlapping interval.

        Parameters
        ----------
        begin: int or float, optional  (default= beginning of the entire impulse graph)
        end: int or float, optional  (default= end of the entire impulse graph)
            Must be bigger than or equal to begin.
        inclusive: 2-tuple boolean that determines inclusivity of begin and end
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

        >>> G = dnx.ImpulseGraph()
        >>> G.add_edges_from([(1, 2, 10), (2, 4, 11), (6, 4, 19), (2, 4, 15)])
        >>> G.nodes()
        [1, 2, 4, 6]

        To get the node data along with the nodes:

        >>> G.add_nodes_from([(1, {'time': '1pm'}), (2, {'time': '2pm'}), (4, {'time': '4pm'}), (6, {'day': 'Friday'})])
        >>> G.nodes(data=True)
        [(1, {'time': '1pm'}), (2, {'time': '2pm'}), (4, {'time': '4pm'}), (6, {'day': 'Friday'})]

        >>> G.nodes(data="time")
        [(1, '1pm'), (2, '2pm'), (4, '4pm'), (6, None)]
        >>> G.nodes(data="time", default="5pm")
        [(1, '1pm'), (2, '2pm'), (4, '4pm'), (6, '5pm')]

        To get nodes which appear in a specific interval.
        Nodes without an edge are not considered present.

        >>> G.nodes(begin=11, data=True)
        [(2, {'time': '2pm'}), (4, {'time': '4pm'}), (6, {'day': 'Friday'})]
        >>> G.nodes(begin=4, end=12)
        [1, 2, 4]
        """

        if begin is None and end is None:
            return NodeDataView(self._node, data=data, default=default)

        inodes = set()
        for edge in self.__search_tree(begin, end, inclusive=inclusive):
            inodes.add(edge[0])
            inodes.add(edge[1])

        node_dict = {n: self._node[n] for n in inodes}

        return NodeDataView(node_dict, data=data, default=default)

    def remove_node(self, n, begin=None, end=None, inclusive=(True, False)):
        """Remove the presence of a node n within the given interval.

        Removes the presence node n and all adjacent edges within the given interval.

        If interval is specified, all the edges of n will be removed within that interval.

        Quiet if n is not in the impulse graph.

        Parameters
        ----------
        n : node
           A node in the graph
        begin: int or float, optional  (default= beginning of the entire impulse graph)
        end: int or float, optional  (default= end of the entire impulse graph)
            Must be bigger than or equal to begin.
        inclusive: 2-tuple boolean that determines inclusivity of begin and end

        Examples
        --------
        >>> G.add_edges_from([(1, 2, 10), (2, 4, 11), (6, 4, 19), (2, 4, 15)])
        >>> G.add_nodes_from([(1, {'time': '1pm'}), (2, {'time': '2pm'}), (4, {'time': '4pm'})])
        >>> G.nodes(begin=10, end=19)
        [1, 2, 4, 6]
        >>> G.remove_node(6, begin=10, end=20)
        >>> G.nodes()
        [1, 2, 4]
        >>> G.nodes(data=True)
        [(1, {'time': '1pm'}), (2, {'time': '2pm'}), (4, {'time': '4pm'})]
        >>> G.remove_node(2)
        >>> G.nodes(data=True)
        [(1, {'time': '1pm'}), (4, {'time': '4pm'})]
        """

        if n not in self._node:
            return

        if begin is None and end is None:
            self._adj.pop(n, None)
            for v in self._adj:
                if n in self._adj[v]:
                    self._adj[v].pop(n, None)

        else:
            remove_edges = []
            for edge in self.__search_tree(begin, end, inclusive):
                if edge[0] == n or edge[1] == n:
                    remove_edges.append(edge)
            for edge in remove_edges:
                self.__remove_iedge(edge)

        # delete the node and its attributes if no edge left
        if n not in self._adj or len(self._adj[n]) == 0:
            self._adj.pop(n, None)
            self._node.pop(n, None)

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

        >>> G = dnx.ImpulseGraph()
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
        self._adj.setdefault(u, {}).setdefault(v, {})[(u, v, t)] = attr
        self._adj.setdefault(v, {}).setdefault(u, {})[(u, v, t)] = attr

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
        >>> G = dnx.ImpulseGraph()
        >>> G.add_edges_from([(1, 2, 10), (2, 4, 11)]) # using a list of edge tuples

        Associate data to edges

        >>> G.add_edges_from([(1, 2, 10), (2, 4, 11)], weight=3)
        >>> G.add_edges_from([(3, 4, 19), (1, 4, 3)], label='WN2898')
        """

        for e in ebunch_to_add:
            if len(e) != 3:
                raise NetworkXError("Edge tuple {0} must be a 3-tuple.".format(e))
            self.add_edge(e[0], e[1], e[2], **attr)

    def has_edge(self, u, v, begin=None, end=None, inclusive=(True, False)):
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
        >>> G = dnx.ImpulseGraph()
        >>> G.add_edges_from([(1, 2, 10), (2, 4, 11)])
        >>> G.has_edge(1, 2)
        True
        >>> G.has_edge(1, 2, begin=2)
        True
        >>> G.has_edge(2, 4, begin=12)
        False
        """
        if u not in self._adj or v not in self._adj[u]:
            return False

        if begin is None and end is None:
            return True

        if begin and end and begin > end:
            raise NetworkXError("IntervalGraph: interval end must be bigger than or equal to begin: "
                                "begin: {}, end: {}.".format(begin, end))

        for iv in self._adj[u][v]:
            if self.__in_interval(iv[2], begin, end, inclusive=inclusive):
                return True
        return False

    def __generate_training_data(self, training_size):
        """Returns list of training samples, X = (node_percent, interval_percent), y = (node_time, interval_time).

        Parameters
        ----------
        trainingSize : int
            Number of samples to generate.
        """

        node_list = list(self._node.keys())
        graph_begin, graph_end = self.interval()
        X = []
        y = []

        while len(X) < training_size:
            node_percent = random.randint(1, 50)
            interval_percent = random.randint(1, 50)
            begin = random.randint(graph_begin,
                                   graph_end - math.ceil((graph_end - graph_begin) * interval_percent / 100))
            nodes = set(random.choices(node_list, k=math.floor(node_percent / 100 * len(node_list))))
            end = begin + (graph_end - graph_begin) * interval_percent / 100

            node_edges = set()
            start_timer = timer()
            for u in nodes:
                for v in self._adj[u]:
                    for edge in self._adj[u][v]:
                        if edge not in node_edges and (edge[2] == begin or (begin < edge[2] < end)):
                            node_edges.add(edge)
            node_time = timer() - start_timer

            if len(node_edges) == 0:
                continue

            interval_edges = []
            start_timer = timer()
            for edge in [(u, v, t) for t in self.tree.irange(begin, end, inclusive=(True, False)) for u, v in self.tree[t]]:
                if edge[0] in nodes or edge[1] in nodes:
                    interval_edges.append(edge)
            interval_time = timer() - start_timer

            X.append((len(nodes) / len(node_list), interval_percent / 100))
            y.append((node_time, interval_time))

        return X, y

    def generate_predictive_model(self, training_size=250):
        """Trains linear regression model used to predict faster ordering of compound slices.

        Parameters
        ----------
        trainingSize : int
            Number of samples to generate.
        """
        X, y = self.__generate_training_data(training_size)

        model = LinearRegression()
        model.fit(X, y)

        self._model = model

    def __edges_node_first(self, u_list, v_list, begin, end):
        # Node filtering
        iedges = set()
        for u, v in product(u_list, v_list):
            if u is None and v is None:
                iedges.update([iv for u in self._adj for v in self._adj[u] for iv in self._adj[u][v]])
            elif u is not None and v is not None:
                if u not in self._adj:
                    continue
                if v not in self._adj[u]:
                    continue
                iedges.update(self._adj[u][v])
            elif u is not None:
                if u not in self._adj:
                    continue
                iedges.update([iv for v in self._adj[u] for iv in self._adj[u][v]])
            else:
                if v not in self._adj:
                    continue
                iedges.update([iv for u in self._adj[v] for iv in self._adj[v][u]])

            # If interval is none, return
            if begin is None and end is None:
                return iedges

            # Interval filtering
            if begin is not None and end is not None and begin > end:
                raise NetworkXError("IntervalGraph: interval end must be bigger than or equal to begin: "
                                    "begin: {}, end: {}.".format(begin, end))

        return [iv for iv in iedges if ImpulseGraph.__overlaps_or_contains(iv, begin, end)]

    def __edges_interval_first(self, begin, end):
        if begin is not None and end is not None and begin > end:
            raise NetworkXError("IntervalGraph: interval end must be bigger than or equal to begin: "
                                "begin: {}, end: {}.".format(begin, end))
        return [(u, v, t) for t in self.tree.irange(begin, end, inclusive=(True, False)) for u, v in self.tree[t]]

    def edges(self, u=None, v=None, begin=None, end=None, inclusive=(True, False), data=False, default=None):
        """Returns a list of Interval objects of the ImpulseGraph edges.

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

        >>> G = dnx.ImpulseGraph()
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

        >>> G = dnx.ImpulseGraph()
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

        try:
            _ = (e for e in u)
        except TypeError:
            u = [u]

        try:
            _ = (e for e in v)
        except TypeError:
            v = [v]

        # Return All
        if u == [None] and v == [None] and begin is None and end is None:
            iedges = self.__edges_node_first(u, v, begin, end)

        # Interval First
        elif u == [None] and v == [None]:
            iedges = self.__edges_interval_first(begin, end)

        # Compound
        elif (u != [None] or v != [None]) and (begin is not None or end is not None) and self._model is not None:
            if u == [None]:
                nodes = v
            elif v == [None]:
                nodes = u
            else:
                nodes = set(*u).union(set(*v))

            node_percent = len(nodes) / self.number_of_nodes()

            graph_begin, graph_end = self.interval()
            if begin is None:
                begin = graph_begin
            if end is None:
                end = graph_end

            interval_percent = (end - begin) / (graph_end - graph_begin)

            node_time, interval_time = self._model.predict([(node_percent, interval_percent)])[0]

            if node_time < interval_time:
                iedges = self.__edges_node_first(u, v, begin, end)
            else:
                iedges = [e for e in self.__edges_interval_first(begin, end) if e[0] in nodes or e[1] in nodes]

        # Node First
        else:
            iedges = self.__edges_node_first(u, v, begin, end)

        # Appending attribute data if needed
        if data is False:
            return iedges if isinstance(iedges, list) else list(iedges)

        if data is True:
            return [(iv, self._adj[iv[0]][iv[1]][iv]) for iv in iedges]

        return [(iv, self._adj[iv[0]][iv[1]][iv][data]) if data in self._adj[iv[0]][iv[1]][iv] else (iv, default) for iv
                in iedges]

    def remove_edge(self, u, v, begin=None, end=None, inclusive=(True, False)):
        """Remove the edge between u and v in the impulse graph,
        during the given interval.

        Quiet if the specified edge is not present.

        Parameters
        ----------
        u, v : nodes
            Nodes can be, for example, strings or numbers.
            Nodes must be hashable (and not None) Python objects.
        begin : int or float, optional (default= beginning of the entire interval graph)
        end : int or float, optional (default= end of the entire interval graph + 1)
            Must be bigger than or equal to begin.
        inclusive: 2-tuple boolean that determines inclusivity of begin and end

        Examples
        --------
        >>> G = dnx.ImpulseGraph()
        >>> G.add_edges_from([(1, 2, 10), (2, 4, 11), (6, 4, 9), (1, 2, 15)])
        >>> G.remove_edge(1, 2)
        >>> G.has_edge(1, 2)
        False

        >>> G = dnx.ImpulseGraph()
        >>> G.add_edges_from([(1, 2, 10), (2, 4, 11), (6, 4, 9), (1, 2, 15)])
        >>> G.remove_edge(1, 2, begin=2, end=11)
        >>> G.has_edge(1, 2, begin=2, end=11)
        False
        >>> G.has_edge(1, 2)
        True
        """

        if u not in self._adj or v not in self._adj[u]:
            return

        iedges_to_remove = []

        # remove every edge between u and v
        if begin is None and end is None:
            for iv in self._adj[u][v]:
                iedges_to_remove.append(iv)

        else:
            for iv in self._adj[u][v]:
                if self.__in_interval(iv[2], begin, end):
                    iedges_to_remove.append(iv)

        # removing found iedges
        for edge in iedges_to_remove:
            self.__remove_iedge(edge)

        # clean up empty dictionaries
        if len(self._adj[u][v]) == 0:
            self._adj[u].pop(v, None)
        if len(self._adj[v][u]) == 0:
            self._adj[v].pop(u, None)
        if len(self._adj[u]) == 0:
            self._adj.pop(u, None)
        if len(self._adj[v]) == 0:
            self._adj.pop(v, None)

    def degree(self, node=None, begin=None, end=None, delta=False, inclusive=(True, False)):
        """Return the degree of a specified node between time begin and end.

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
        >>> G = dnx.ImpulseGraph()
        >>> G.add_edge(1, 2, 3)
        >>> G.add_edge(2, 3, 8)
        >>> G.degree(2)
        2
        >>> G.degree(2, 2)
        2
        >>> G.degree(2, end=8)
        1
        >>> G.degree()
        1.33333
        >>> G.degree(2, delta=True)
        [(3, 1), (8, 1)]
        """
        if end is None:
            inclusive = (inclusive[0], True)
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
            return len(self.edges(u=node, begin=begin, end=end, inclusive=inclusive))

        # delta == True, return list of changes
        d = {}
        output = []

        # for each edge determine if the begin and/or end value is in specified time period
        for edge in self.edges(u=node, begin=begin, end=end, inclusive=inclusive):
            d.setdefault(edge[2], []).append((edge[0], edge[1]))

        # for each time in Dict add to output list the len of each value
        for time in d:
            output.append((time, len(d[time])))

        return output

    def __remove_iedge(self, iedge):
        """Remove the interval edge from the impulse graph.

        Quiet if the specified edge is not present.

        Parameters
        ----------
        iedge : Edge Tuple (u,v,eid,t)
            Edge to be removed.
        """
        try:
            self.tree[iedge[2]].remove((iedge[0], iedge[1]))
            del self._adj[iedge[0]][iedge[1]][iedge]
            del self._adj[iedge[1]][iedge[0]][iedge]
        except:
            return
        print(self._adj)

    def __validate_interval(self, begin=None, end=None):
        """Returns validated begin and end.
        Raises an exception if begin is larger than end.

        Parameters
        ----------
        begin : int or float, optional
        end : int or float, optional
        """

        if (begin is not None and end is not None) and begin > end:
            raise NetworkXError("ImpulseGraph: interval end must be bigger than or equal to begin: "
                                "begin: {}, end: {}.".format(begin, end))

        return begin, end

    def __search_tree(self, begin=None, end=None, inclusive=(True, False)):
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
            for u, v in self.tree[t]:
                yield (u, v, t)

    def __in_interval(self, t, begin, end, inclusive=(True, False)):
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
            return t >= begin and t <= end
        if inclusive == (True, False):
            return t >= begin and t < end
        if inclusive == (False, True):
            return t > begin and t <= end
        if inclusive == (False, False):
            return t > begin and t < end

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
        <class 'networkx.classes.graph.Graph'>
        >>> list(H.edges(data=True))
        [(1, 2, {}), (2, 4, {})]

        >>> H = G.to_subgraph(10, 12, edge_timestamp_data=True)
        >>> type(H)
        <class 'networkx.classes.graph.Graph'>
        >>> list(H.edges(data=True))
        [(1, 2, {'timestamp': 10}), (2, 4, {'timestamp': 11})]

        >>> M = G.to_subgraph(4, 12, multigraph=True, edge_timestamp_data=True)
        >>> type(M)
        <class 'networkx.classes.multigraph.MultiGraph'>
        >>> list(M.edges(data=True))
        [(1, 2, {'timestamp': 10}), (2, 4, {'timestamp': 11})]
        """
        iedges = self.__search_tree(begin, end, inclusive=inclusive)

        if multigraph:
            G = MultiGraph()
        else:
            G = Graph()

        if edge_data and edge_timestamp_data:
            G.add_edges_from((iedge[0], iedge[1], dict(self._adj[iedge[0]][iedge], timestamp=iedge[2]))
                             for iedge in iedges)
        elif edge_data:
            G.add_edges_from((iedge[0], iedge[1], self._adj[iedge[0]][iedge[1]][iedge])
                             for iedge in iedges)
        elif edge_timestamp_data:
            G.add_edges_from((iedge[0], iedge[1], {'timestamp': iedge[2]})
                             for iedge in iedges)
        else:

            G.add_edges_from((iedge[0], iedge[1]) for iedge in iedges)

        if node_data:
            G.add_nodes_from((n, self._node[n].copy()) for n in G.nodes)

        return G

    def to_snapshots(self, number_of_snapshots=False, length_of_snapshots=False, multigraph=False, edge_data=False,
                     edge_timestamp_data=False,
                     node_data=False, return_length=False):
        """Return a list of networkx Graph or MultiGraph objects as snapshots
        of the impulse graph in consecutive order.

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
        to_subgraph : subgraph based on an interval
        to_snapshotgraph : snapshotgraph based on impulse graph

        Notes
        -----
        In order to create snapshots, timestamp of edges of the impulse graph must be numbers.

        If multigraph= False, and edge_data=True or edge_timestamp_data=True,
        in case there are multiple edges, only one will show with one of the edge's attributes.

        Examples
        --------
        Snapshots of NetworkX Graph

        >>> G = dnx.ImpulseGraph()
        >>> G.add_edges_from([(1, 2, 10), (2, 4, 11), (6, 4, 19), (2, 4, 15)])
        >>> S, l = G.to_snapshots(2, edge_timestamp_data=True, return_length=True)
        >>> S
        [<networkx.classes.graph.Graph object at 0x100000>, <networkx.classes.graph.Graph object at 0x150d00>]
        >>> l
        4.5
        >>> for g in S:
        >>> ... g.edges(data=True))
        [(1, 2, {'timestamp': 10}), (2, 4, {'timestamp': 11})]
        [(2, 4, {'timestamp': 15}), (4, 6, {'timestamp': 19})]

        Snapshots of NetworkX MultiGraph

        >>> S, l = G.to_snapshots(3, multigraph=True, edge_timestamp_data=True, return_length=True)
        >>> S
        [<networkx.classes.multigraph.MultiGraph object at 0x1060d40b8>, <networkx.classes.multigraph.MultiGraph object at 0x151020c9e8>, <networkx.classes.multigraph.MultiGraph object at 0x151021d390>]
        >>> l
        3.0
        >>> for g in S:
        >>> ... g.edges(data=True))
        [(1, 2, {'timestamp': 10}), (2, 4, {'timestamp': 11})]
        [(2, 4, {'timestamp': 15})]
        [(6, 4, {'timestamp': 19})]
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
        inclusive = (True, False)
        for i in range(number_of_snapshots):
            if i == number_of_snapshots - 1:
                inclusive = (True, True)
            snapshots.append(
                self.to_subgraph(begin + length_of_snapshots * i,
                                 begin + length_of_snapshots * (i + 1), inclusive=inclusive,
                                 multigraph=multigraph, edge_data=edge_data, edge_timestamp_data=edge_timestamp_data,
                                 node_data=node_data))
        if return_length:
            return snapshots, length_of_snapshots

        return snapshots

    def to_snapshot_graph(self, multigraph=False, edge_data=False, edge_timestamp_data=False, node_data=False):
        """
        Return a dnx.SnapshotGraph of the impulse graph.

        Parameters
        ----------
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

        See Also
        --------
        to_snapshots : divide the impulse graph to snapshots

        Notes
        -----
        In order to create snapshots, timestamp of edges of the impulse graph must be numbers.

        If multigraph= False, and edge_data=True or edge_timestamp_data=True,
        in case there are multiple edges, only one will show with one of the edge's attributes.

        Examples
        --------
        Snapshots of NetworkX Graph

        >>> G = dnx.ImpulseGraph()
        >>> G.add_edges_from([(1, 2, 10), (2, 3, 11), (2, 4, 11), (4, 6, 19)])
        >>> S = G.to_snapshot_graph(edge_timestamp_data=True)
        >>> for g in S:
        >>> ... g.edges(data=True))
        [(1, 2, {'timestamp': 10})]
        [(2, 3, {'timestamp': 11}), (2, 4, {'timestamp': 11})]
        [(4, 6, {'timestamp': 19})]

        Snapshots of NetworkX MultiGraph

        >>> S = G.to_snapshot_graph(multigraph=True, edge_timestamp_data=True)
        >>> for g in S:
        >>> ... g.edges(data=True))
        [(1, 2, {'timestamp': 10}), (1, 2, {'timestamp': 10})]
        [(2, 3, {'timestamp': 11}), (2, 3, {'timestamp': 11}), (2, 4, {'timestamp': 11}), (2, 4, {'timestamp': 11})]
        [(4, 6, {'timestamp': 19}), (4, 6, {'timestamp': 19})]
        """

        G = dnx.SnapshotGraph()

        for time, snapshot in self.tree.items():
            G.insert(graph=self.to_subgraph(time, time, inclusive=(True, True), multigraph=multigraph,
                                            edge_data=edge_data, edge_timestamp_data=edge_timestamp_data,
                                            node_data=node_data),
                     time=time)

        return G

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
        if begin is None and end is None:
            return True
        if begin is None:
            return iv[2] < end
        if end is None:
            return iv[2] >= begin
        return (begin < iv[2] < end and iv[2]) or iv[2] == begin

    @staticmethod
    def from_networkx_graph(graph, timestamp='timestamp'):
        """Convert a NetworkX Graph to a ImpulseGraph.

        Parameters
        ----------
        graph : NetworkX Graph

        timestamp : string
        Attribute for timestamp in NetworkX Graph.

        Returns
        -------
        G: ImpulseGraph
            The graph corresponding to the lines in edge list.

        Examples
        --------

        graph = nx.Graph()
        graph.add_edge(1,2,timestamp=10,weight=1.5)
        graph.add_edge(2,3,timestamp=11)

        ig = ImpulseGraph.from_networkx_graph(graph)
      """

        G = ImpulseGraph()

        for edge in graph.edges(data=True):
            attr = {}

            for key in edge[2]:
                if key != timestamp:
                    attr[key] = edge[2][key]

            G.add_edge(edge[0], edge[1], edge[2][timestamp], **attr)

        return G

    @staticmethod
    def load_from_txt(path, delimiter=" ", nodetype=int, timestamptype=float, order=('u', 'v', 't'), predict=False, comments="#"):
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

        predict : bool, optional (default= False)
        If true, calls generate_predictive_model, after graph is created.

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

        G = ImpulseGraph()

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

                line = line.rstrip().split(delimiter)

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

        if predict is True:
            G.generate_predictive_model()

        return G

    def save_to_txt(self, path, delimiter=" "):
        """Write impulse graph to path.
           Every line in the file must be an edge in the following format: "node node timestamp".
           Timestamps must be integers or floats.
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
                line = str(edge[0][0]) + delimiter + str(edge[0][1]) + delimiter + str(edge[0][2])
                for key in edge[1]:
                    line += delimiter + str(key) + '=' + str(edge[1][key])
                line += '\n'

                file.write(line)
