from dynetworkx.classes.intervalgraph import IntervalGraph
from networkx.classes.digraph import DiGraph
from networkx.classes.multidigraph import MultiDiGraph

import dynetworkx as dnx
from networkx.exception import NetworkXError
from dynetworkx.classes.intervaltree import IntervalTree
from sortedcontainers import SortedList, SortedDict
import random
import math
from timeit import default_timer as timer
from sklearn.linear_model import LinearRegression
from itertools import product

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
        self._model = None

        self.graph.update(attr)

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
        >>> G = dnx.IntervalDiGraph()
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
        self._pred.setdefault(node_for_adding, {})
        self._succ.setdefault(node_for_adding, {})

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

        # if edge exists, just update attr
        if u in self._pred and v in self._succ and v in self._pred[u] and u in self._succ[v] and (u, v, begin, end) in self._pred[u][v] and (u, v, begin, end) in self._succ[v][u]:
            self._pred[u][v][(u, v, begin, end)].update(attr)
            self._succ[v][u][(u, v, begin, end)].update(attr)
            return

        iedge = (u, v, begin, end)

        # add nodes

        self._pred.setdefault(u, {}).setdefault(v, {})
        self._succ.setdefault(v, {}).setdefault(u, {})
        self._node.setdefault(u, {})
        self._node.setdefault(v, {})

        # add edge
        try:
            self.tree.add(iedge)
        except ValueError:
            raise NetworkXError("IntervalDiGraph: edge duration must be strictly bigger than zero {0}.".format(iedge))

        self._pred[u][v][iedge] = self._succ[v][u][iedge] = attr

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

        if u not in self._pred:
            return False
        if v not in self._pred[u]:
            return False

        if begin is None and end is None:
            if v in self._pred[u]:
                return True
            return False

        if not overlapping:
            if begin is None or end is None:
                raise NetworkXError("For exact interval match (overlapping=False), both begin and end must be defined.")

            return self.edges(u, v, begin, end) is not None

        if begin and end and begin > end:
            raise NetworkXError("IntervalDiGraph: interval end must be bigger than or equal to begin: "
                                "begin: {}, end: {}.".format(begin, end))

        for iv in self._pred[u][v]:
            if self.__overlaps_or_contains(iv, begin, end):
                return True
        return False

    def __edges_node_first(self, u_list, v_list, begin, end):
        # Node filtering
        iedges = set()
        for u, v in product(u_list, v_list):
            if u is None and v is None:
                iedges.update([iv for u in self._pred for v in self._pred[u] for iv in self._pred[u][v]])
            elif u is not None and v is not None:
                if u not in self._pred:
                    continue
                if v not in self._pred[u]:
                    continue
                iedges.update(self._pred[u][v])
            elif u is not None:
                if u not in self._pred:
                    continue
                iedges.update([iv for v in self._pred[u] for iv in self._pred[u][v]])
            else:
                if v not in self._succ:
                    continue
                iedges.update([iv for u in self._succ[v] for iv in self._succ[v][u]])

            # If interval is none, return
            if begin is None and end is None:
                return iedges

            # Interval filtering
            if begin is not None and end is not None and begin > end:
                raise NetworkXError("IntervalDiGraph: interval end must be bigger than or equal to begin: "
                                    "begin: {}, end: {}.".format(begin, end))

        return [iv for iv in iedges if IntervalDiGraph.__overlaps_or_contains(iv, begin, end)]

    def __edges_interval_first(self, begin, end):
        if begin is not None and end is not None and begin > end:
            raise NetworkXError("IntervalDiGraph: interval end must be bigger than or equal to begin: "
                                "begin: {}, end: {}.".format(begin, end))
        return self.tree[begin:end]

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

            node_time, interval_time = self._model.predict((node_percent, interval_percent))[0]

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
            return [(iv, self._pred[iv[0]][iv[1]][iv]) for iv in iedges]

        return [(iv, self._pred[iv[0]][iv[1]][iv][data]) if data in self._pred[iv[0]][iv[1]][iv] else (iv, default) for iv
                in iedges]

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
                if u in self._pred:
                    for v in self._pred[u]:
                        for edge in self._pred[u][v]:
                            if edge not in node_edges and (edge[2] == begin or (edge[2] > begin and edge[3] < end)):
                                node_edges.add(edge)
            node_time = timer() - start_timer

            if len(node_edges) == 0:
                continue

            interval_edges = []
            start_timer = timer()
            for edge in self.tree[begin:end]:
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

        if u not in self._pred or v not in self._pred[u]:
            return

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
            for iv in self._pred[u][v]:
                iedges_to_remove.append(iv)

        # remove edge between u and v with overlapping interval with the given interval
        else:
            if begin and end and begin > end:
                raise NetworkXError("IntervalDiGraph: interval end must be bigger than or equal to begin: "
                                "begin: {}, end: {}.".format(begin, end))

            for iv in self._pred[u][v]:
                if IntervalDiGraph.__overlaps_or_contains(iv, begin, end):
                    iedges_to_remove.append(iv)

        # removing found iedges
        for iv in iedges_to_remove:
            self.__remove_iedge(iv)

        # clean up empty dictionaries
        if len(self._pred[u][v]) == 0:
            self._pred[u].pop(v, None)
        if len(self._succ[v][u]) == 0:
            self._succ[v].pop(u, None)
        if len(self._pred[u]) == 0:
            self._pred.pop(u, None)
        if len(self._succ[v]) == 0:
            self._succ.pop(v, None)

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
        if node is None:
            n = 0
            l = 0
            for node in self.nodes(begin=begin, end=end):
                n += 1
                l += self.degree(node, begin=begin, end=end)
            return l / n

        # specified node, no degree_change, return degree
        if delta is False:
            return len(self.edges(u=node, begin=begin, end=end)) + \
                   len(self.edges(v=node, begin=begin, end=end))

        # delta == True, return list of changes
        if begin is None:
            begin = self.tree.begin
        if end is None:
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
        >>> G = dnx.IntervalDiGraph()
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
            raise NetworkXError("IntervalDiGraph: interval end must be bigger than or equal to begin: "
                                "begin: {}, end: {}.".format(begin, end))
        iedges = self.tree[begin:end]

        if multigraph:
            G = MultiDiGraph()
        else:
            G = DiGraph()

        if edge_data and edge_interval_data:
            G.add_edges_from((iedge.data[0], iedge.data[1],
                              dict(self._pred[iedge.data[0]][iedge], begin=iedge.begin, end=iedge.end))
                             for iedge in iedges)
        elif edge_data:
            G.add_edges_from((iedge.data[0], iedge.data[1], self._pred[iedge.data[0]][iedge].copy())
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
        self._pred[iedge[0]][iedge[1]].pop(iedge, None)
        self._succ[iedge[1]][iedge[0]].pop(iedge, None)

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
        if begin is None and end is None:
            return True
        if begin is None:
            return iv[2] < end
        if end is None:
            return iv[3] > begin
        return (iv[2] < end and iv[3] > begin) or iv[2] == begin
