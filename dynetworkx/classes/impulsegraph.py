import dynetworkx as dnx
from networkx.classes.graph import Graph
from networkx.exception import NetworkXError
from sortedcontainers import SortedDict
from networkx.classes.multigraph import MultiGraph
from networkx.classes.reportviews import NodeView, EdgeView, NodeDataView


class ImpulseGraph(object):
    """Base class for undirected interval graphs.

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
    Create an empty graph structure (a "null interval graph") with no nodes and
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

    >>> G = dnx.IntervalGraph(day="Friday")
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

    def __init__(self, name='',**attr):
        """Initialize an interval graph with edges, name, or graph attributes.

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
        self.name = name
        self.edgeid = 0
        
        self.graph.update(attr)

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
        return self.tree.keys()[0], self.tree.keys()[-1]

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
        
        self._node.setdefault(node_for_adding,attr).update(attr)
        self._adj.setdefault(node_for_adding,{})

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
            if isinstance(n,tuple) and isinstance(n[1],dict):
                self.add_node(n[0],**attr)
                self._node[n[0]].update(n[1])
            else: self.add_node(n,**attr)

    def number_of_nodes(self, begin=None, end=None, inclusive=(True,True)):
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
        4
        """

        if begin is None and end is None:
            return len(self._node)

        inodes = set()
        for edge in self.__search_tree(begin, end,inclusive=inclusive):
            inodes.add(edge[0])
            inodes.add(edge[1])
            
        return len(inodes)

    def has_node(self, n, begin=None, end=None, inclusive=(True,True)):
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
        
        if n not in G._node:
            return False

        if begin is None and end is None:
            return True
        
        begin, end = self.__validate_interval(begin, end)

        inodes = set()
        for edge in self.__search_tree(begin, end,inclusive=inclusive):
            inodes.add(edge[0])
            inodes.add(edge[1])
                
        if n in inodes:
            return True
        return False
        
    def nodes(self, begin=None, end=None, inclusive=(True,True),data=False, default=None):
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
        for edge in self.__search_tree(begin, end,inclusive=inclusive):
                inodes.add(edge[0])
                inodes.add(edge[1])

        node_dict = {n:self._node[n] for n in inodes}

        return NodeDataView(node_dict, data=data, default=default)

    def remove_node(self, n, begin=None, end=None, inclusive=(True,True)):
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
            for iedge in list(self._adj[n].keys()):
                self.__remove_iedge(iedge)
        else:
            remove_edges = []
            for edge in self.__search_tree(begin, end,inclusive=inclusive):
                if edge[0] == n or edge[1] == n:
                    remove_edges.append(edge)
            for edge in remove_edges:
                self.__remove_iedge(edge)

        # delete the node and its attributes if no edge left
        if len(self._adj[n]) == 0:
            del self._adj[n]
            del self._node[n]

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
        
        eid = self.edgeid
        self.tree.setdefault(t,set()).add((u,v,eid))

        self._node.setdefault(u,{})
        self._node.setdefault(v,{})
        self._adj.setdefault(u,{})[(u,v,eid,t)] = attr
        self._adj.setdefault(v,{})[(u,v,eid,t)] = attr

        self.edgeid += 1

    def add_edges_from(self, ebunch_to_add, **attr):
        """Add all the edges in ebunch_to_add.

        Parameters
        ----------
        ebunch_to_add : container of edges
            Each edge given in the container will be added to the
            interval graph. The edges must be given as as 3-tuples (u, v, t).
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

    def has_edge(self, u, v, begin=None, end=None, inclusive=(True,True)):
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

        if begin is None and end is None:
            for edge in self._adj[u].keys():
                if edge[1] == v:
                    return True
            return False

        begin, end = self.__validate_interval(begin, end)

        for edge in self._adj[u].keys():
            if edge[1] == v and __inInterval(edge[3],begin, end, inclusive=inclusive):
                return True
        return False

    def edges(self, u=None, v=None, begin=None, end=None, inclusive=(True,True), data=False, default=None):
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

        >>> G = dnx.IntervalGraph()
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
        
        iedges = []
        for edge in self.__search_tree(begin, end, inclusive=inclusive):
            if u is not None and v is not None:
                if u == edge[0] and v == edge[1]:
                    iedges.append(edge)
            elif u is not None:
                if u == edge[0]:
                    iedges.append(edge)
            else:
                iedges.append(edge)

        if data is False:
            return [(edge[0],edge[1],edge[3]) for edge in iedges]

        if data is True:
            return [((edge[0],edge[1],edge[3]), self._adj[edge[0]][edge]) for edge in iedges]

        return [((edge[0],edge[1],edge[3]), self._adj[edge[0]][edge][data]) if data in self._adj[edge[0]][edge]
                else ((edge[0],edge[1],edge[3]),default) for edge in iedges]
    
    def remove_edge(self, u, v, begin=None, end=None, inclusive=(True,True)):
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
        
        iedges = []
        for edge in self.__search_tree(begin, end, inclusive=inclusive):
            if u == edge[0] and v == edge[1]:
                iedges.append(edge)

        for edge in iedges:
            self.__remove_iedge(edge)
            
    def degree(self, node=None, begin=None, end=None, delta=False):
        """Return the degree of a specified node between time begin and end.

        Parameters
        ----------
        node : Nodes can be, for example, strings or numbers.
            Nodes must be hashable (and not None) Python objects.
        begin : int or float, optional (default= beginning of the entire impulse graph)
            Inclusive beginning time of the edge appearing in the impulse graph.
        end : int or float, optional (default= end of the entire impulse graph)
            Non-inclusive ending time of the edge appearing in the impulse graph.

        Returns
        -------
        Integer value of degree of specified node.

        Examples
        --------
        >>> G = ImpulseGraph()
        >>> G.add_edge(1, 2, 3)
        >>> G.add_edge(2, 3, 8)
        >>> G.degree(2)
        2
        >>> G.degree(2,2)
        2
        >>> G.degree(2,end=8)
        1
        >>> G.mean_degree()
        1.33333
        >>> G.degree(2,delta=True)
        [(8, 1), (3, 1)]
        """
        #no specified node, return mean degree
        if node == None:
            n = 0
            l = 0
            for node in self.nodes(begin=begin, end=end):
                n += 1
                l += self.degree(node,begin=begin,end=end)
            return l/n

        #specified node, no degree_change, return degree
        if delta == False:
            return len(self.edges(u=node, begin=begin, end=end))

        #delta == True, return list of changes
        if begin == None:
            begin = list(self.tree.keys())[0]
        if end == None:
            end = list(self.tree.keys())[-1]

        d = {}
        output = []

        #for each edge determine if the begin and/or end value is in specified time period
        for edge in self.edges(u=node,begin=begin,end=end,inclusive=(True,True)):
            d.setdefault(edge[2],[]).append((edge[0],edge[1]))

        #for each time in Dict add to output list the len of each value
        for time in d:
            output.append((time,len(d[time])))
                
        return output
    
    def __remove_iedge(self, iedge):
        """Remove the interval edge from the impulse graph.

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
            self.tree[t].remove((u,v,eid))
            del self._adj[u][iedge]
            del self._adj[v][iedge]
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
            raise NetworkXError("ImpulseGraph: interval end must be bigger than or equal to begin: "
                                "begin: {}, end: {}.".format(begin, end))

        return begin, end

    def __search_tree(self, begin=None, end=None, inclusive=(True,True)):
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
                yield (*edge,t)
            
        for t in self.tree.irange(begin,end,inclusive=inclusive):
            for edge in self.tree[t]:
                yield (*edge,t)

    def to_subgraph(self, begin, end, inclusive=(True,True), multigraph=False, edge_data=False, edge_timestamp_data=False, node_data=False):
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
            G.add_edges_from((iedge[0], iedge[1], dict(self._adj[iedge[0]][iedge], timestamp=iedge[3]))
                             for iedge in iedges)
        elif edge_data:
            G.add_edges_from((iedge[0], iedge[1], self._adj[iedge.data[0]][iedge].copy())
                             for iedge in iedges)
        elif edge_timestamp_data:
            G.add_edges_from((iedge[0], iedge[1], {'timestamp':iedge[3]})
                             for iedge in iedges)
        else:

            G.add_edges_from((iedge[0], iedge[1]) for iedge in iedges)

        if node_data:
            G.add_nodes_from((n, self._node[n].copy()) for n in G.nodes)

        return G

    def to_snapshots(self, number_of_snapshots, multigraph=False, edge_data=False, edge_timestamp_data=False, node_data=False, return_length=False):
        """Return a list of networkx Graph or MultiGraph objects as snapshots
        of the impulse graph in consecutive order.

        Parameters
        ----------
        number_of_snapshots : integer
            Number of snapshots to divide the interval graph into.
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
                                 multigraph=multigraph, edge_data=edge_data, edge_timestamp_data=edge_timestamp_data,
                                 node_data=node_data))
        if return_length:
            return snapshots, snapshot_len

        return snapshots

    @staticmethod
    def load_from_txt(path, delimiter=" ", nodetype=None, timestamptype=float, comments="#"):
        """Read impulse graph in from path.
           Every line in the file must be an edge in the following format: "node node timestamp".
           Timestamps must be integers or floats.
           Nodes can be any hashable objects.

        Parameters
        ----------
        path : string or file
           Filename to read.

        nodetype : Python type, optional
           Convert nodes to this type.

        timestamptype : Python type, optional (default= float)
        Convert timestamp to this type.
        This must be an orderable type, ideally int or float. Other orderable types have not been fully tested.

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

        with open(path, 'r') as file:
            for line in file:
                p = line.find(comments)
                if p >= 0:
                    line = line[:p]
                if not len(line):
                    continue

                line = line.rstrip().split(delimiter)

                u = line[0]
                v = line[1]
                t = line[2]

                edgedata = {}
                for data in line[3:]:
                    key, value = data.split('=')
                    edgedata[key] = value

                if nodetype is not None:
                    try:
                        u = nodetype(u)
                        v = nodetype(v)
                    except:
                        raise TypeError("Failed to convert node to {0}".format(nodetype))

                try:
                    t = timestamptype(t)
                except:
                    raise TypeError("Failed to convert interval time to {}".format(timestamptype))

                G.add_edge(u,v,t,**edgedata)

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

    def __inInterval(t,begin,end,inclusive=(True,True)):
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
            begin = float('inf')
        if end is None:
            end = float('-inf')

        if inclusive == (True,True):
            return t >= begin and t <= end
        if inclusive == (True,False):
            return t >= begin and t < end
        if inclusive == (False,True):
            return t > begin and t <= end
        if inclusive == (False,False):
            return t > begin and t < end
