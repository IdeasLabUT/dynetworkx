from networkx import NetworkXError
from sortedcontainers import SortedDict

from dynetworkx.classes.intervalgraph import IntervalGraph
from dynetworkx.classes.intervaltree import IntervalTree
from networkx.classes.digraph import DiGraph
from networkx.classes.multidigraph import MultiDiGraph


class IntervalDiGraph(IntervalGraph):

    def __init__(self, **attr):
        """Initialize an interval graph with edges, name, or graph attributes.

        Parameters
        ----------
        attr : keyword arguments, optional (default= no attributes)
            Attributes to add to graph as key=value pairs.

        Examples
        --------
        >>> G = dnx.IntervalDiGraph()
        >>> G = dnx.IntervalDiGraph(name='my graph')
        >>> G.graph
        {'name': 'my graph'}
        """
        self.tree = IntervalTree()
        self.graph = {}  # dictionary for graph attributes
        self._node = {}
        self._pred = {}  # out
        self._succ = {}  # in

        self.graph.update(attr)

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

        >>> G = dnx.IntervalDiGraph()
        >>> e = (1, 2, 3, 10)
        >>> G.add_edge(1, 2, 3, 10)           # explicit two-node form with interval
        >>> G.add_edge(*e)             # single edge as tuple of two nodes and interval
        >>> G.add_edges_from([(1, 2, 3, 10)])  # add edges from iterable container

        Associate data to edges using keywords:

        >>> G.add_edge(1, 2, 3, 10 weight=3)
        >>> G.add_edge(1, 3, 4, 9, weight=7, capacity=15, length=342.7)
        """

        iedge = self.edges(u, v, begin, end, data=True)

        # if edge exists, just update attr
        if iedge:
            self._pred[u][iedge].update(attr)
            self._succ[v][iedge].update(attr)
            return

        iedge = (u, v, begin, end)

        # add nodes

        self._pred.setdefault(u, {})
        self._succ.setdefault(v, {})
        self._node.setdefault(u, {})
        self._node.setdefault(v, {})

        # add edge
        try:
            self.tree.add(iedge)
        except ValueError:
            raise NetworkXError("IntervalDiGraph: edge duration must be strictly bigger than zero {0}.".format(iedge))

        self._pred[u][iedge] = self._succ[v][iedge] = attr

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
        >>> G = dnx.IntervalDiGraph()
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
        >>> G = dnx.IntervalDiGraph()
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
            for iv in self._pred[u].keys():
                if iv[1] == v:
                    return True
            return False

        if not overlapping:
            if begin is None or end is None:
                raise NetworkXError("For exact interval match (overlapping=False), both begin and end must be defined.")

            return self.edges(u, v, begin, end) is not None

        if begin and end and begin > end:
            raise NetworkXError("IntervalGraph: interval end must be bigger than or equal to begin: "
                                "begin: {}, end: {}.".format(begin, end))

        for iv in self._pred[u].keys():
            if iv[1] == v and self.__overlaps_or_contains(iv, begin, end):
                return True
        return False

    def edges(self, u=None, v=None, begin=None, end=None, data=False, default=None):
        """Returns a list of Interval objects of the IntervalDiGraph edges.

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

        >>> G = dnx.IntervalDiGraph()
        >>> G.add_edges_from([(1, 2, 3, 10), (2, 4, 1, 11), (6, 4, 12, 19), (2, 4, 8, 15)])
        >>> G.edges()
        [(1, 2, 3, 10), (2, 4, 1, 11), (6, 4, 12, 19), (2, 4, 8, 15)]

        To get edges which appear in a specific interval:

        >>> G.edges(begin=10)
        [(1, 2, 3, 10), (2, 4, 1, 11), (6, 4, 12, 19), (2, 4, 8, 15)]
        >>> G.edges(end=5)
        [(1, 2, 3, 10), (2, 4, 1, 11)]
        >>> G.edges(begin=2, end=4)
        (1, 2, 3, 10), (2, 4, 1, 11)

        To get edges with either of the two nodes being defined:

        >>> G.edges(u=2)
        [(2, 4, 1, 11), (2, 4, 8, 15)]
        >>> G.edges(u=2, begin=11)
        [(2, 4, 8, 15)]
        >>> G.edges(u=2, v=4, end=8)
        [(2, 4, 1, 11)]
        >>> G.edges(u=1, v=6)
        []

        To get a list of edges with data:

        >>> G = dnx.IntervalDiGraph()
        >>> G.add_edge(1, 3, 1, 4, weight=8, height=18)
        >>> G.add_edge(1, 2, 3, 10, weight=10)
        >>> G.add_edge(2, 6, 2, 10)
        >>> G.edges(data="weight")
        [(2, 6, 2, 10)), None), (1, 2, 3, 10), 10), (1, 3, 1, 4), 8)]
        >>> G.edges(data="weight", default=5)
        [(2, 6, 2, 10)), 5), (1, 2, 3, 10), 10), (1, 3, 1, 4), 8)]
        >>> G.edges(data=True)
        [(2, 6, 2, 10)), {}), (1, 2, 3, 10), {weight:10}), (1, 3, 1, 4), {weight:8, height:18})]
        >>> G.edges(u=1, begin=5, end=9, data="weight")
        [(1, 2, 3, 10), 10)]
        """
        # If non of the nodes are defined the interval tree is queried for the list of edges,
        # otherwise the edges are returned based on the nodes in the self._adj.o

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
                if u not in self._pred:
                    return []
                if v not in self._succ:
                    return []

                iedges = [iv for iv in self._pred[u].keys() if iv[1] == v]
            elif u:
                if u not in self._pred:
                    return []
                iedges = self._pred[u].keys()
            else:
                if v not in self._succ:
                    return []
                iedges = self._succ[v].keys()

            # Interval filtering
            if begin and end and begin > end:
                raise NetworkXError("IntervalGraph: interval end must be bigger than or equal to begin: "
                                    "begin: {}, end: {}.".format(begin, end))
            iedges = [iv for iv in iedges if IntervalDiGraph.__overlaps_or_contains(iv, begin, end)]

        # Appending attribute data if needed
        if data is False:
            return iedges if isinstance(iedges, list) else list(iedges)

        if data is True:
            return [(iv, self._pred[iv[0]][iv]) for iv in iedges]

        return [(iv, self._pred[iv[0]][iv][data]) if data in self._pred[iv[0]][iv].keys() else
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
        >>> G = dnx.IntervalDiGraph()
        >>> G.add_edges_from([(1, 2, 3, 10), (2, 4, 1, 11), (6, 4, 5, 9), (1, 2, 8, 15)])
        >>> G.remove_edge(1, 2)
        >>> G.has_edge(1, 2)
        False

        With specific overlapping interval

        >>> G = dnx.IntervalDiGraph()
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
            for iv in self._pred[u].keys():
                if iv[1] == v:
                    iedges_to_remove.append(iv)

        # remove edge between u and v with overlapping interval with the given interval
        if begin and end and begin > end:
            raise NetworkXError("IntervalGraph: interval end must be bigger than or equal to begin: "
                                "begin: {}, end: {}.".format(begin, end))

        for iv in self._pred[u].keys():
            if iv[1] == v and IntervalDiGraph.__overlaps_or_contains(iv, begin, end):
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
        >>> G = IntervalDiGraph()
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
            return len(self.edges(u=node, begin=begin, end=end)) + \
                   len(self.edges(v=node, begin=begin, end=end))

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
        for edge in self.edges(v=node, begin=begin, end=end):
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

        return sorted(output)

    def in_degree(self, node=None, begin=None, end=None, delta=False):
        """Return the in-degree of a specified node between time begin and end.

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
        >>> G = IntervalDiGraph()
        >>> G.add_edge(1, 2, 3, 5)
        >>> G.add_edge(2, 3, 8, 11)
        >>> G.in_degree(2)
        1
        >>> G.in_degree(2, 2)
        1
        >>> G.in_degree(2, end=8)
        1
        >>> G.in_degree()
        1
        >>> G.in_degree(2, delta=True)
        [(3, 1), (5, 0)]
        """

        # no specified node, return mean degree
        if node == None:
            n = 0
            l = 0
            for node in self.nodes(begin=begin, end=end):
                n += 1
                l += self.in_degree(node, begin=begin, end=end)
            return l / n

        # specified node, no degree_change, return degree
        if delta == False:
            return len(self.edges(v=node, begin=begin, end=end))

        # delta == True, return list of changes
        if begin == None:
            begin = self.tree.begin
        if end == None:
            end = self.tree.end

        current_degree = self.in_degree(node, begin=begin, end=begin)
        sd = SortedDict()
        output = []

        # for each edge determine if the begin and/or end value is in specified time period
        for edge in self.edges(v=node, begin=begin, end=end):
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

        return sorted(output)

    def out_degree(self, node=None, begin=None, end=None, delta=False):
        """Return the out-degree of a specified node between time begin and end.

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
        >>> G = IntervalDiGraph()
        >>> G.add_edge(1, 2, 3, 5)
        >>> G.add_edge(2, 3, 8, 11)
        >>> G.degree(2)
        1
        >>> G.out_degree(2,2)
        1
        >>> G.out_degree(2,end=8)
        0
        >>> G.out_degree()
        0.666666
        >>> G.out_degree(2,delta=True)
        [(8, 1)]
        """

        # no specified node, return mean degree
        if node == None:
            n = 0
            l = 0
            for node in self.nodes(begin=begin, end=end):
                n += 1
                l += self.out_degree(node, begin=begin, end=end)
            return l / n

        # specified node, no degree_change, return degree
        if delta == False:
            return len(self.edges(u=node, begin=begin, end=end))

        # delta == True, return list of changes
        if begin == None:
            begin = self.tree.begin
        if end == None:
            end = self.tree.end

        current_degree = self.out_degree(node, begin=begin, end=begin)
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
                    print(time, begin, edge, current_degree)
                output.append((time[0], current_degree))

        return sorted(output)

    def to_networkx_graph(self, begin, end, multigraph=False, edge_data=False, edge_interval_data=False, node_data=False):
        """Return a networkx DiGraph or MultiDiGraph which includes all the nodes and
        edges which have overlapping intervals with the given interval.

        Wrapper function for IntervalDiGraph.to_subgraph. Refer to IntervalDiGraph.to_subgraph for full description.
        """
        return self.to_subgraph(begin=begin, end=end, multigraph=multigraph, edge_data=edge_data, edge_interval_data=edge_interval_data, node_data=node_data)

    def to_subgraph(self, begin, end, multigraph=False, edge_data=False, edge_interval_data=False, node_data=False):
        """Return a networkx DiGraph or MultiDiGraph which includes all the nodes and
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
        <class 'networkx.classes.graph.DiGraph'>
        >>> list(H.edges(data=True))
        [(1, 2, {}), (2, 4, {})]

        >>> H = G.to_subgraph(4, 12, edge_interval_data=True)
        >>> type(H)
        <class 'networkx.classes.graph.DiGraph'>
        >>> list(H.edges(data=True))
        [(1, 2, {'end': 10, 'begin': 3}), (2, 4, {'end': 15, 'begin': 8})]

        >>> M = G.to_subgraph(4, 12, multigraph=True, edge_interval_data=True)
        >>> type(M)
        <class 'networkx.classes.multigraph.MultiDiGraph'>
        >>> list(M.edges(data=True))
        [(1, 2, {'end': 10, 'begin': 3}), (2, 4, {'end': 11, 'begin': 1}), (2, 4, {'end': 15, 'begin': 8})]
        """
        if begin and end and begin > end:
            raise NetworkXError("IntervalGraph: interval end must be bigger than or equal to begin: "
                                "begin: {}, end: {}.".format(begin, end))
        iedges = self.tree[begin:end]

        if multigraph:
            G = MultiDiGraph()
        else:
            G = DiGraph()

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

    def __remove_iedge(self, iedge):
        """Remove the interval edge from the interval graph.

        Quiet if the specified edge is not present.

        Parameters
        ----------
        iedge : Interval object
            Interval edge to be removed.

        Examples
        --------
        >>> G = dnx.IntervalDiGraph()
        >>> G.add_edge(1, 2, 3, 10)
        >>> iedge = (1, 2, 3, 10)
        >>> G.__remove_iedge(iedge)
        """
        self.tree.remove(iedge)
        self._pred[iedge[0]].pop(iedge, None)
        self._succ[iedge[1]].pop(iedge, None)


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
        # need to check for iv.contains(begin) in case begin == end
        if not begin and not end:
            return True
        if not begin:
            return iv[2] < end
        if not end:
            return iv[3] > begin
        return (iv[2] < end and iv[3] > begin) or iv[2] == begin
