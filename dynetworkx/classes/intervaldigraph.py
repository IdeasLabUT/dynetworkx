from networkx import NetworkXError
from sortedcontainers import SortedDict

from dynetworkx.classes.intervalgraph import IntervalGraph
from intervaltree import IntervalTree, Interval


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

        iedge = self.__get_iedge_in_tree(u, v, begin, end)

        # if edge exists, just update attr
        if iedge is not None:
            self._pred[u][iedge].update(attr)
            self._succ[v][iedge].update(attr)
            return

        iedge = Interval(begin, end, (u, v))

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
                if iv.data[1] == v:
                    return True
            return False

        if not overlapping:
            if begin is None or end is None:
                raise NetworkXError("For exact interval match (overlapping=False), both begin and end must be defined.")

            return self.__get_iedge_in_tree(u, v, begin, end) is not None

        begin, end = self.__validate_interval(begin, end)

        for iv in self._pred[u].keys():
            if iv.data[1] == v and iv.overlaps(begin=begin, end=end):
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

        >>> G = dnx.IntervalDiGraph()
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
        iedges = []
        if u is None and v is None:
            if begin is None and end is None:
                iedges = self.tree.all_intervals
            # interval filtering
            else:
                iedges = self.__search_tree(begin, end)

        else:
            # Node filtering
            if u is not None and v is not None:
                iedges = [iv for iv in self._pred[u].keys() if iv.data[1] == v]
            elif u is not None and u in self._pred:
                iedges = self._pred[u].keys()
            elif v in self._succ:
                iedges = self._succ[v].keys()

            # Interval filtering
            begin, end = self.__validate_interval(begin, end)
            iedges = [iv for iv in iedges if IntervalDiGraph.__overlaps_or_contains(iv, begin, end)]

        # Appending attribute data if needed
        if data is False:
            return iedges if isinstance(iedges, list) else list(iedges)

        if data is True:
            return [(iv, self._pred[iv.data[0]][iv]) for iv in iedges]

        return [(iv, self._pred[iv.data[0]][iv][data]) if data in self._pred[iv.data[0]][iv].keys() else
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

            iedge = self.__get_iedge_in_tree(u, v, begin, end)
            if iedge is not None:
                self.__remove_iedge(iedge)
            return

        iedges_to_remove = []

        # remove every edge between u and v
        if begin is None and end is None:
            for iv in self._pred[u].keys():
                if iv.data[1] == v:
                    iedges_to_remove.append(iv)

        # remove edge between u and v with overlapping interval with the given interval
        begin, end = self.__validate_interval(begin, end)

        for iv in self._pred[u].keys():
            if iv.data[1] == v and IntervalDiGraph.__overlaps_or_contains(iv, begin, end):
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
            begin = self.tree.begin()
        if end == None:
            end = self.tree.end()

        current_degree = self.degree(node, begin=begin, end=begin)
        sd = SortedDict()
        output = []

        # for each edge determine if the begin and/or end value is in specified time period
        for edge in self.edges(u=node, begin=begin, end=end):
            if edge.begin >= begin:
                # if begin is in specified time period, add to SortedDict, with +1 to indicate begin
                sd.setdefault((edge.begin, 1), []).append(edge.data)
            if edge.end < end:
                # if begin is in specified time period, add to SortedDict, with -1 to indicate begin
                sd.setdefault((edge.end, -1), []).append(edge.data)
        for edge in self.edges(v=node, begin=begin, end=end):
            if edge.begin >= begin:
                # if begin is in specified time period, add to SortedDict, with +1 to indicate begin
                sd.setdefault((edge.begin, 1), []).append(edge.data)
            if edge.end < end:
                # if begin is in specified time period, add to SortedDict, with -1 to indicate begin
                sd.setdefault((edge.end, -1), []).append(edge.data)

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
            begin = self.tree.begin()
        if end == None:
            end = self.tree.end()

        current_degree = self.in_degree(node, begin=begin, end=begin)
        sd = SortedDict()
        output = []

        # for each edge determine if the begin and/or end value is in specified time period
        for edge in self.edges(v=node, begin=begin, end=end):
            if edge.begin >= begin:
                # if begin is in specified time period, add to SortedDict, with +1 to indicate begin
                sd.setdefault((edge.begin, 1), []).append(edge.data)
            if edge.end < end:
                # if begin is in specified time period, add to SortedDict, with -1 to indicate begin
                sd.setdefault((edge.end, -1), []).append(edge.data)

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
            begin = self.tree.begin()
        if end == None:
            end = self.tree.end()

        current_degree = self.out_degree(node, begin=begin, end=begin)
        sd = SortedDict()
        output = []

        # for each edge determine if the begin and/or end value is in specified time period
        for edge in self.edges(u=node, begin=begin, end=end):
            if edge.begin >= begin:
                # if begin is in specified time period, add to SortedDict, with +1 to indicate begin
                sd.setdefault((edge.begin, 1), []).append(edge.data)
            if edge.end < end:
                # if begin is in specified time period, add to SortedDict, with -1 to indicate begin
                sd.setdefault((edge.end, -1), []).append(edge.data)

        for time in sd:
            for edge in sd[time]:
                # iterate through SortedDict, only advancing current degree if edge was not counted on init
                if time[0] != begin:
                    current_degree += time[1]
                    print(time, begin, edge, current_degree)
                output.append((time[0], current_degree))

        return sorted(output)

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
        >>> iedge = Interval(3, 10, (1, 2))   # Interval(begin, end, (u, v))
        >>> G.__remove_iedge(iedge)
        """
        self.tree.discard(iedge)
        self._pred[iedge.data[0]].pop(iedge, None)
        self._succ[iedge.data[1]].pop(iedge, None)

    def __get_iedge_in_tree(self, u, v, begin, end):
        """Return interval edge if found in the interval graph with the exact interval,
        otherwise return None.

        Parameters
        ----------
        u, v : nodes
            Nodes can be, for example, strings or numbers.
            Nodes must be hashable (and not None) Python objects.
        begin : int or float
            Inclusive beginning time of the edge appearing in the interval graph.
        end : int or float
            Non-inclusive ending time of the edge appearing in the interval graph.
            Must be bigger than begin.

        Examples
        --------
        >>> G = dnx.IntervalDiGraph()
        >>> G.add_edge(1, 2, 3, 10)
        >>> G.__get_iedge_in_tree(2, 1, 3, 10)
        Interval(3, 10, (1, 2))
        >>> G.__get_iedge_in_tree(2, 1, 4, 10)
        None
        """

        temp_iedge = Interval(begin, end, (u, v))
        if temp_iedge in self.tree:
            return temp_iedge

        return None

    def __validate_interval(self, begin=None, end=None):
        """Returns validated begin and end.
        Replaces begin with the begin time of the graph if None is passed.
        Replaces end with the end time of the graph + 1 (to make it inclusive) if None is passed.
        Raises an exception if begin is larger than end.

        Parameters
        ----------
        begin : int or float, optional
            Inclusive beginning time of the edge appearing in the interval graph.
        end : int or float, optional
            Non-inclusive ending time of the edge appearing in the interval graph.
        """
        if begin is None:
            begin = self.tree.begin()

        if end is None:
            end = self.tree.end() + 1

        if begin > end:
            raise NetworkXError("IntervalDiGraph: interval end must be bigger than or equal to begin: "
                                "begin: {}, end: {}.".format(begin, end))

        return begin, end

    def __search_tree(self, begin=None, end=None):
        """if begin and end are equal performs a point search on the tree,
        otherwise an interval search is performed.

       Parameters
       ----------
       begin: int or float, optional  (default= beginning of the entire interval graph)
            Inclusive beginning time of the node appearing in the interval graph.
        end: int or float, optional  (default= end of the entire interval graph + 1)
            Non-inclusive ending time of the node appearing in the interval graph.
            Must be bigger than or equal begin.
            Note that the default value is shifted up by 1 to make it an inclusive end.
       """
        begin, end = self.__validate_interval(begin, end)
        if begin != end:
            return self.tree[begin:end]
        return self.tree[begin]

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
        return iv.overlaps(begin, end) or iv.contains_point(begin)
