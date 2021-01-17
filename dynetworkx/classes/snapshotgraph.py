from networkx.classes.graph import Graph
import numpy as np
from networkx import adjacency_matrix, from_numpy_array
from sortedcontainers import SortedDict, SortedList
import copy


class SnapshotGraph(object):
    def __init__(self, **attr):
        self.graph = {}
        self.graph.update(attr)
        self.snapshots = SortedDict()

    @property
    def name(self):
        """String identifier of the snapshot graph.

        This snapshot graph attribute appears in the attribute dict SnapshotGraph.graph
        keyed by the string `"name"`. as well as an attribute (technically
        a property) `SnapshotGraph.name`. This is entirely user controlled.
        """
        return self.graph.get('name', '')

    @name.setter
    def name(self, s):
        self.graph['name'] = s

    def __str__(self):
        """Return the snapshot graph name.

        Returns
        -------
        name : string
            The name of the snapshot graph.

        Examples
        --------
        >>> G = dnx.SnapshotGraph(name='foo')
        >>> str(G)
        'foo'
        """
        return self.name

    def __len__(self):
        """Return the number of snapshots. Use: 'len(G)'.

        Returns
        -------
        num_snapshots : int
            The number of snapshots in the graph.

        Examples
        --------
        >>> nxG1 = nx.Graph()
        >>> nxG2 = nx.Graph()
        >>>
        >>> nxG1.add_edges_from([(1, 2), (1, 3)])
        >>> nxG2.add_edges_from([(1, 4), (1, 3)])
        >>>
        >>> G = dnx.SnapshotGraph()
        >>> G.add_snapshot(graph=nxG1)
        >>> G.add_snapshot(graph=nxG2)
        >>> len(G)
        2

        """
        return len(self.snapshots)

    def __contains__(self, graph):
        """Return True if graph in the snapshot graph, False otherwise. Use: 'graph in G'.

        Parameters
        ----------
        graph: networkx graph object
            networkx graph to be looked for into snapshot graph.

        Returns
        -------
        None

        Examples
        --------
        >>> nxG1 = nx.Graph()
        >>> nxG2 = nx.Graph()
        >>>
        >>> nxG1.add_edges_from([(1, 2), (1, 3)])
        >>> nxG2.add_edges_from([(1, 4), (1, 3)])
        >>>
        >>> G = dnx.SnapshotGraph()
        >>> G.add_snapshot(graph=nxG1)
        >>> G.add_snapshot(graph=nxG2)
        >>> nxG1 in G
        True
        """

        try:
            return graph in self.snapshots.values()
        except TypeError:
            return False

    def __iter__(self):
        """Iterates through snapshots in snapshot graph.


        Returns
        -------
        Iterable of snapshots

        Examples
        --------
        >>> nxG1 = nx.Graph()
        >>> nxG2 = nx.Graph()
        >>>
        >>> nxG1.add_edges_from([(1, 2), (1, 3)])
        >>> nxG2.add_edges_from([(1, 4), (1, 3)])
        >>>
        >>> G = dnx.SnapshotGraph()
        >>> G.add_snapshot(graph=nxG1)
        >>> G.add_snapshot(graph=nxG2)
        >>> for snapshot in G:
                print(True)
        True
        True
        """

        return iter(self.snapshots.values())

    def insert(self, graph, start=None, end=None, time=None):
        """Insert a graph into the snapshot graph, with specified intervals.

        Parameters
        ----------
        graph: networkx graph object
            A networkx graph to be inserted into snapshot graph.
        start: start of the interval, inclusive
        end: end of the interval, exclusive
        time: timestamp for impulses, cannot be used together with (start, end)

        Returns
        -------
        None

        Examples
        --------
        >>> nxG1 = nx.Graph()
        >>> nxG1.add_edges_from([(1, 2), (1, 3)])
        >>> G = dnx.SnapshotGraph()
        >>> G.insert(nxG1, start=0, end=3)

        """
        if time and (start or end):
            raise ValueError('Time and (start or end) cannot both be specified.')
        elif time:
            self.snapshots.update({(time, time): graph})
        elif (start is None and end is not None) or (start is not None and end is None):
            raise ValueError('Start and end must both be specified for intervals.')
        elif start > end:
            raise ValueError('Start of the interval must be lower or equal to end')
        else:
            self.snapshots.update({(start, end): graph})

    def add_snapshot(self, ebunch=None, graph=None, start=None, end=None, time=None):
        """Add a snapshot with a bunch of edge values.

        Parameters
        ----------
        ebunch : container of edges, optional (default= None)
            Each edge in the ebunch list will be included to all added graphs.
        graph : networkx graph object, optional (default= None)
            networkx graph to be inserted into snapshot graph.
        start: start timestamp, inclusive
        end: end timestamp, exclusive
        time: timestamp for impulses, cannot be used together with (start, end)

        Returns
        -------
        None

        Examples
        --------
        >>> G = dnx.SnapshotGraph()
        >>> G.add_snapshot([(1, 4), (1, 3)], start=0, end=3)
        """
        if not graph:
            g = Graph()
            g.add_edges_from(ebunch)
        else:
            g = graph

        if time and (start or end):
            raise ValueError('Time and (start or end) cannot both be specified.')
        elif time:
            self.insert(g, time=time)
        elif (start is None and end is not None) or (start is not None and end is None):
            raise ValueError('Start and end must both be specified for intervals.')
        else:
            self.insert(g, start=start, end=end)

    def subgraph(self, nbunch, sbunch=None, start=None, end=None):
        """Return a snapshot graph containing only the nodes in bunch, and snapshot indexes in sbunch.

        Parameters
        ----------
        nbunch : container of nodes
            Each node in the nbunch list will be included in all subgraphs indexed in sbunch.
        sbunch : container of edges, optional (default= None)
            Each snapshot index in this list will be included in the returned list
            of subgraphs. It is highly recommended that this list is sequential,
            however it can be out of order.
        start: start timestamp, inclusive
        end: end timestamp, exclusive

        Returns
        -------
            snap_graph : SnapshotGraph object
                Contains only the nodes in bunch, and snapshot indexes in sbunch.

        Examples
        --------
        >>> G = dnx.SnapshotGraph()
        >>> G.add_snapshot([(1, 2), (2, 3), (4, 6), (2, 4)], start=0, end=3)
        >>> G.add_snapshot([(1, 2), (2, 3), (4, 6), (2, 4)], start=3, end=10)
        >>> H = G.subgraph([4, 6])
        >>> type(H)
        <class 'snapshotgraph.SnapshotGraph'>
        >>> list(H.get([0])[0].edges(data=True))
        [(4, 6, {})]
        """

        subgraph = SnapshotGraph()
        subgraph.graph = self.graph

        if sbunch and (start or end):
            raise ValueError('Either sbunch or (start and end) can be specified.')
        elif sbunch:
            for key, snapshot in self._get(sbunch=sbunch):
                subgraph.add_snapshot(graph=snapshot.subgraph(nbunch), start=key[0], end=key[1])
        else:
            for key, snapshot in self._get(start=start, end=end, include_interval=True):
                subgraph.add_snapshot(graph=snapshot.subgraph(nbunch), start=key[0], end=key[1])

        return subgraph

    def degree(self, sbunch=None, nbunch=None, start=None, end=None, weight=None):
        """Return a list of tuples containing the degrees of each node in each snapshot

        Parameters
        ----------
        sbunch : container of snapshot indexes, optional (default= None)
            Each snapshot index in this list will be included in the returned list
            of node degrees. It is highly recommended that this list is sequential,
            however it can be out of order.
        nbunch : container of nodes, optional (default= None)
            Each node in the nbunch list will be included in the returned list of
            node degrees.
        start: start timestamp, inclusive
        end: end timestamp, exclusive
        weight : string, optional (default= None)
            The edge attribute that holds the numerical value used as a weight. If None, then each edge has weight 1.
            The degree is the sum of the edge weights adjacent to the node.

        Returns
        -------
            degree_list : list
                List of DegreeView objects containing the degree of each node, indexed by requested snapshot.

        Examples
        --------
        >>> G = dnx.SnapshotGraph()
        >>> G.add_snapshot([(1, 2), (1, 3)], start=0, end=3)
        >>> G.add_snapshot([(1, 4), (1, 3)], start=3. end=10)
        >>> G.degree(sbunch=[1])
        [DegreeView({1: 2, 4: 1, 3: 1})]
        >>> G.degree(nbunch=[1, 2])
        [DegreeView({1: 2, 2: 1}), DegreeView({1: 2})]
        """
        # returns a list of degrees for each graph snapshot in snapshots
        # use generator to create list of degrees

        if sbunch and (start or end):
            raise ValueError('Either sbunch or (start and end) can be specified.')
        elif sbunch:
            if nbunch:
                return [graph.degree(nbunch, weight=weight) for graph in self._get(sbunch=sbunch)]
            else:
                return [graph.degree(graph, weight=weight) for graph in self._get(sbunch=sbunch)]
        else:
            if nbunch:
                return [graph.degree(nbunch, weight=weight) for graph in self._get(start=start, end=end)]
            else:
                return [graph.degree(graph, weight=weight) for graph in self._get(start=start, end=end)]

    def number_of_nodes(self, sbunch=None, start=None, end=None):
        """Gets number of nodes in each snapshot requested in 'sbunch'.

        Parameters
        ----------
        sbunch : container of snapshot indexes, optional (default= None)
            Each snapshot index in this list will be included in the returned list
            of number of nodes in the snapshot. It is highly recommended that this list is sequential,
            however it can be out of order.
        start: start timestamp, inclusive
        end: end timestamp, exclusive

        Returns
        -------
            num_nodes : list
                A list of of the number of nodes in each requested snapshot.

        Examples
        --------
        >>> G = dnx.SnapshotGraph()
        >>> G.add_snapshot([(1, 2), (1, 3)], start=0, end=3)
        >>> G.add_snapshot([(1, 4), (1, 3)], start=3, end=10)
        >>> G.number_of_nodes(sbunch=[1])
        [3]
        >>> G.number_of_nodes(sbunch=[0, 1])
        [3, 3]
        """
        # returns a list of the number of nodes in each graph in the range

        if sbunch and (start or end):
            raise ValueError('Either sbunch or (start and end) can be specified.')
        elif sbunch:
            return [graph.number_of_nodes() for graph in self._get(sbunch=sbunch)]
        else:
            return [graph.number_of_nodes() for graph in self._get(start=start, end=end)]

    def order(self, sbunch=None, start=None, end=None):
        """Returns order of each graph requested in 'sbunch'.

        Parameters
        ----------
        sbunch : container of snapshot indexes, optional (default= None)
            Each snapshot index in this list will be included in the returned list
            of node orders. It is highly recommended that this list is sequential,
            however it can be out of order.
        start: start timestamp, inclusive
        end: end timestamp, exclusive

        Returns
        -------
            snapshot_orders : list
                A list of the orders of each snapshot.

        Examples
        --------
        >>> G = dnx.SnapshotGraph()
        >>> G.add_snapshot([(1, 2), (1, 3)], start=0, end=3)
        >>> G.add_snapshot([(1, 4), (1, 3)], start=3, end=10)
        >>> G.order(sbunch=[1])
        [3]
        >>> G.order(sbunch=[0, 1])
        [3, 3]
        """
        # returns a list of the order of the graph in the range

        if sbunch and (start or end):
            raise ValueError('Either sbunch or (start and end) can be specified.')
        elif sbunch:
            return [graph.order() for graph in self._get(sbunch=sbunch)]
        else:
            return [g.order() for g in self._get(start=start, end=end)]

    def has_node(self, n, sbunch=None, start=None, end=None):
        """Gets boolean list of if a snapshot in 'sbunch' contains node 'n'.

        Parameters
        ----------
        n : node
            Node to be checked for in requested snapshots.
        sbunch : container of snapshot indexes, optional (default= None)
            Each snapshot index in this list will be included in the returned list
            of if the snapshot graph includes the node. It is highly recommended
            that this list is sequential, however it can be out of order.
        start: start timestamp, inclusive
        end: end timestamp, exclusive

        Returns
        -------
            List of boolean values if index in sbunch contains n.

        Examples
        --------
        >>> G = dnx.SnapshotGraph()
        >>> G.add_snapshot([(1, 2), (1, 3)], start=0, end=3)
        >>> G.add_snapshot([(1, 4), (1, 3)], start=3, end=10)
        >>> G.has_node(1, sbunch=[1])
        [True]
        >>> G.has_node(1)
        [True, True]

        """

        if sbunch and (start or end):
            raise ValueError('Either sbunch or (start and end) can be specified.')
        elif sbunch:
            return [graph.has_node(n) for graph in self._get(sbunch=sbunch)]
        else:
            return [graph.has_node(n) for graph in self._get(start=start, end=end)]

    def is_multigraph(self, sbunch=None, start=None, end=None):
        """Returns a list of boolean values for if the graph at the index is a multigraph.

        Parameters
        ----------
        sbunch : container of snapshot indexes, optional (default= None)
            Each snapshot index in this list will be included in the returned list
            of booleans. It is highly recommended that this list is sequential,
            however it can be out of order.
        start: start timestamp, inclusive
        end: end timestamp, exclusive

        Returns
        -------
            mutli_list : list
                List of boolean values if index in sbunch is a multigraph.

        Examples
        --------
        >>> G = dnx.SnapshotGraph()
        >>> G.add_snapshot([(1, 2), (1, 3)], start=0, end=3)
        >>> G.add_snapshot([(1, 4), (1, 3)], start=3, end=10)
        >>> G.is_multigraph(sbunch=[0, 1])
        [False, False]
        >>> G.is_multigraph()
        [False, False]

        """

        if sbunch and (start or end):
            raise ValueError('Either sbunch or (start and end) can be specified.')
        elif sbunch:
            return [graph.is_multigraph() for graph in self._get(sbunch=sbunch)]
        else:
            return [graph.is_multigraph() for graph in self._get(start=start, end=end)]

    def is_directed(self, sbunch=None, start=None, end=None):
        """Returns a list of boolean values for if the graph at the index is a directed graph.

        Parameters
        ----------
        sbunch : container of snapshot indexes, optional (default= None)
            Each snapshot index in this list will be included in the returned list
            of booleans. It is highly recommended that this list is sequential,
            however it can be out of order.
        start: start timestamp, inclusive
        end: end timestamp, exclusive

        Returns
        -------
            is_direct_list : list
                List of boolean values if index in sbunch is a directed graph.

        Examples
        --------
        >>> G = dnx.SnapshotGraph()
        >>> G.add_snapshot([(1, 2), (1, 3)], start=0, end=3)
        >>> G.add_snapshot([(1, 4), (1, 3)], start=3, end=10)
        >>> G.is_directed(sbunch=[0, 1])
        [False, False]
        >>> G.is_directed()
        [False, False]

        """

        if sbunch and (start or end):
            raise ValueError('Either sbunch or (start and end) can be specified.')
        elif sbunch:
            return [graph.is_directed() for graph in self._get(sbunch=sbunch)]
        else:
            return [graph.is_directed() for graph in self._get(start=start, end=end)]

    def to_directed(self, sbunch=None, start=None, end=None):
        """Returns a list of networkx directed graph objects.

        Parameters
        ----------
        sbunch : container of snapshot indexes, optional (default= None)
            Each snapshot index in this list will be included in the returned list
            of directed graphs. It is highly recommended that this list is sequential,
            however it can be out of order.
        start: start timestamp, inclusive
        end: end timestamp, exclusive

        Returns
        -------
            direct_list : list
                List of networkx directed graph objects.

        Examples
        --------
        >>> G = dnx.SnapshotGraph()
        >>> G.add_snapshot([(1, 2), (1, 3)], start=0, end=3)
        >>> G.add_snapshot([(1, 4), (1, 3)], start=3, end=10)
        >>> G.to_directed(sbunch=[0, 1])
        [<networkx.classes.digraph.DiGraph object at 0x7f1a6de49dd8>, <networkx.classes.digraph.DiGraph object at 0x7f1a6de49e10>]

        """

        if sbunch and (start or end):
            raise ValueError('Either sbunch or (start and end) can be specified.')
        elif sbunch:
            return [graph.to_directed() for graph in self._get(sbunch=sbunch)]
        else:
            return [graph.to_directed() for graph in self._get(start=start, end=end)]

    def to_undirected(self, sbunch=None, start=None, end=None, ):
        """Returns a list of networkx graph objects.

        Parameters
        ----------
        sbunch : container of snapshot indexes, optional (default= None)
            Each snapshot index in this list will be included in the returned list
            of undirected graphs. It is highly recommended that this list is sequential,
            however it can be out of order.
        start: start timestamp, inclusive
        end: end timestamp, exclusive

        Returns
        -------
            undirect_list : list
                List of networkx graph objects.

        Examples
        --------
        >>> G = dnx.SnapshotGraph()
        >>> G.add_snapshot([(1, 2), (1, 3)], start=0, end=3)
        >>> G.add_snapshot([(1, 4), (1, 3)], start=3, end=10)
        >>> G.to_directed(sbunch=[0, 1])
        [<networkx.classes.graph.Graph object at 0x7ff532219e10>, <networkx.classes.graph.Graph object at 0x7ff532219e48>]

        """

        if sbunch and (start or end):
            raise ValueError('Either sbunch or (start and end) can be specified.')
        elif sbunch:
            return [graph.to_undirected() for graph in self._get(sbunch=sbunch)]
        else:
            return [graph.to_undirected() for graph in self._get(start=start, end=end)]

    def size(self, sbunch=None, start=None, end=None, weight=None):
        """Returns the size of each graph index as specified in sbunch as a list.

        Parameters
        ----------
        sbunch : container of snapshot indexes, optional (default= None)
            Each snapshot index in this list will be included in the returned list
            of sizes. It is highly recommended that this list is sequential,
            however it can be out of order.
        start: start timestamp, inclusive
        end: end timestamp, exclusive
        weight : string, optional (default=None)
            The edge attribute that holds the numerical value used as a weight.
            If None, then each edge has weight 1.

        Returns
        -------
            size_list: list
                List of sizes of each graph indexed in sbunch.

        Examples
        --------
        >>> G = dnx.SnapshotGraph()
        >>> G.add_snapshot([(1, 2), (1, 3)], start=0, end=3)
        >>> G.add_snapshot([(1, 4), (1, 3)], start=3, end=10)
        >>> G.size(sbunch=[0, 1])
        [2, 2]
        >>> G.size()
        [2, 2]

        """

        if sbunch and (start or end):
            raise ValueError('Either sbunch or (start and end) can be specified.')
        elif sbunch:
            return [graph.size(weight=weight) for graph in self._get(sbunch=sbunch)]
        else:
            return [graph.size(weight=weight) for graph in self._get(start=start, end=end)]

    def _get(self, sbunch=None, start=None, end=None, include_interval=False, split_overlaps=False):
        """Returns a list of graphs specified in sbunch. Hidden utility tool for other functions.

        Parameters
        ----------
        sbunch : container of snapshot indexes, optional (default= None)
            Each snapshot index in this list will be included in the returned list
            of graphs. It is highly recommended that this list is sequential,
            however it can be out of order.
        start: start timestamp, inclusive
        end: end timestamp, exclusive
        include_interval: if True, return snapshots with its corresponding intervals
        split_overlaps: if True, when query by time interval, split snapshots if query interval overlaps with any
            snapshots' intervals. For ex: graph G contains snapshots with time intervals [(0,4),(4,6),(6,10)]. If query
            interval is [2,10], the snapshot with interval (0,4) will be split into two snapshots (0,2) and (2,4), both
            of which have the same copy of the original snapshot. This parameter is used for updating graphs by
            interval. For intance, with the example above, if you want to update interval (2,10), then the snapshot at
            (0,2) won't be updated.

        Returns
        -------
        If include_interval: List of tuples of (interval, networkx graph object).
        else: List of networkx graph objects.

        Examples
        --------
        >>> G = dnx.SnapshotGraph()
        >>> G.add_snapshot([(1, 2), (1, 3)], start=0, end=3)
        >>> G.add_snapshot([(1, 4), (1, 3)], start=3, end=10)
        >>> G._get(sbunch=[0])
        [<networkx.classes.graph.Graph object at 0x7f27f5bd39b0>]
        >>> G._get()
        [<networkx.classes.graph.Graph object at 0x7f27f5bd39b0>, <networkx.classes.graph.Graph object at 0x7f27f5bd3d30>]
        >>> G._get(start=2, end=6)
        [<networkx.classes.graph.Graph object at 0x7f27f5bd39b0>, <networkx.classes.graph.Graph object at 0x7f27f5bd3d30>]
        """

        if include_interval:
            graphs = self.snapshots.items()
        else:
            graphs = self.snapshots.values()

        if sbunch and (start or end):
            raise ValueError('Either sbunch or (start and end) can be specified.')
        elif sbunch:  # if retrieve by indexes
            for index in sbunch:
                yield graphs[index]
        else:  # if retrieve by interval
            if start is None:
                min_idx = 0
            else:
                min_idx = self.snapshots.bisect_left((start,))

                # Decrease 1 index if start is in the middle of an interval
                # Eg: if Keys = [(2,5)(5,6)], start=3 won't retrieve (2,5) as we want,
                # therefore, decrease 1 index to include (2,5). If start=5, then we won't need to change
                if min_idx > 0 and start < self.snapshots.keys()[min_idx][0]:
                    if split_overlaps:
                        # Eg: if Keys = [(2,5)(5,6)] and start=3, split (2,5) into (2,3) and (3,5)
                        key, g = self.snapshots.popitem(min_idx - 1)
                        self.insert(g, key[0], start)
                        self.insert(copy.deepcopy(g), start, key[1])
                    else:
                        min_idx -= 1

            if end is None:
                max_idx = len(self.snapshots)
            else:
                max_idx = self.snapshots.bisect_left((end,))
                # Split the snapshot if 'end' is in the middle of an interval
                # Eg: if Keys = [(2,5)(5,9)] and end=7, split (5,9) into (5,7) and (7,9)
                if split_overlaps and max_idx < len(self.snapshots) and end < self.snapshots.keys()[max_idx][1]:
                    key, g = self.snapshots.popitem(max_idx)
                    self.insert(g, key[0], end)
                    self.insert(copy.deepcopy(g), end, key[1])

            for graph in graphs[min_idx: max_idx]:
                yield graph

    def get(self, sbunch=None, start=None, end=None):
        """Returns a list of graphs specified in sbunch. Interface function for users.

        Parameters
        ----------
        sbunch : container of snapshot indexes, optional (default= None)
            Each snapshot index in this list will be included in the returned list
            of graphs. It is highly recommended that this list is sequential,
            however it can be out of order.
        start: start timestamp, inclusive
        end: end timestamp, exclusive

        Returns
        -------
        List of networkx graph objects.


        Examples
        --------
        >>> G = dnx.SnapshotGraph()
        >>> G.add_snapshot([(1, 2), (1, 3)], start=0, end=3)
        >>> G.add_snapshot([(1, 4), (1, 3)], start=3, end=10)
        >>> G._get(sbunch=[0])
        [<networkx.classes.graph.Graph object at 0x7f27f5bd39b0>]
        >>> G._get()
        [<networkx.classes.graph.Graph object at 0x7f27f5bd39b0>, <networkx.classes.graph.Graph object at 0x7f27f5bd3d30>]
        >>> G._get(start=2, end=6)
        [<networkx.classes.graph.Graph object at 0x7f27f5bd39b0>, <networkx.classes.graph.Graph object at 0x7f27f5bd3d30>]
        """

        return [snapshot for snapshot in self._get(sbunch, start, end)]

    def add_nodes_from(self, nbunch, sbunch=None, start=None, end=None, **attrs):
        """Adds nodes to snapshots in sbunch.
        Note: This function may lead to increase in number of snapshots if changes occur within a snapshot.

        Parameters
        ----------
        nbunch : container of nodes
            Each node in the nbunch list will be added to all graphs indexed in sbunch.
        sbunch : container of snapshot indexes, optional (default= None)
            Each snapshot index in this list will be included in the returned list
            of node degrees. It is highly recommended that this list is sequential,
            however it can be out of order.
        start: start timestamp, inclusive
        end: end timestamp, exclusive

        Returns
        -------
        None

        Examples
        --------
        >>> G = dnx.SnapshotGraph()
        >>> G.add_snapshot([(1, 2), (1, 3)], start=0, end=3)
        >>> G.add_snapshot([(1, 4), (1, 3)], start=3, end=10)

        >>> G.add_nodes_from([5, 6, 7], [0])
        >>> G.add_nodes_from([8, 9, 10, 11], [1])
        >>> nx.adjacency_matrix(G.get()[0]).todense()
        [[0 1 1 0 0 0]
         [1 0 0 0 0 0]
         [1 0 0 0 0 0]
         [0 0 0 0 0 0]
         [0 0 0 0 0 0]
         [0 0 0 0 0 0]]
        >>> nx.adjacency_matrix(G.get()[1]).todense()
        [[0 1 1 0 0 0 0]
         [1 0 0 0 0 0 0]
         [1 0 0 0 0 0 0]
         [0 0 0 0 0 0 0]
         [0 0 0 0 0 0 0]
         [0 0 0 0 0 0 0]
         [0 0 0 0 0 0 0]]

        """
        
        if sbunch and (start or end):
            raise ValueError('Either sbunch or (start and end) can be specified.')
        elif sbunch:
            for graph in self._get(sbunch=sbunch):
                graph.add_nodes_from(nbunch, **attrs)
        else:
            for graph in self._get(start=start, end=end, split_overlaps=True):
                graph.add_nodes_from(nbunch, **attrs)

    def add_edges_from(self, ebunch, sbunch=None, start=None, end=None, **attrs):
        """Adds edges to snapshots in sbunch.
        Note: This function may lead to increase in number of snapshots if changes occur within a snapshot.

        Parameters
        ----------
        ebunch : container of edges
            Each edge in the ebunch list will be added to all graphs indexed in sbunch.
        sbunch : container of snapshot indexes, optional (default= None)
            Each snapshot index in this list will be included in the returned list
            of node degrees. It is highly recommended that this list is sequential,
            however it can be out of order.
        start: start timestamp, inclusive
        end: end timestamp, exclusive

        Returns
        -------
        None

        Examples
        --------
        >>> G = dnx.SnapshotGraph()
        >>> G.add_snapshot([(1, 2), (1, 3)], start=0, end=3)
        >>> G.add_snapshot([(1, 4), (1, 3)], start=3, end=10)

        >>> G.add_edges_from([(5, 6), (7, 6)], [0])
        >>> G.add_edges_from([(8, 9), (10, 11)], [0, 1])
        >>> nx.adjacency_matrix(G.get()[0]).todense()
        [[0 1 1 0 0 0 0 0 0 0]
         [1 0 0 0 0 0 0 0 0 0]
         [1 0 0 0 0 0 0 0 0 0]
         [0 0 0 0 1 0 0 0 0 0]
         [0 0 0 1 0 1 0 0 0 0]
         [0 0 0 0 1 0 0 0 0 0]
         [0 0 0 0 0 0 0 1 0 0]
         [0 0 0 0 0 0 1 0 0 0]
         [0 0 0 0 0 0 0 0 0 1]
         [0 0 0 0 0 0 0 0 1 0]]
        >>> nx.adjacency_matrix(G.get()[1]).todense()
        [[0 1 1 0 0 0 0]
         [1 0 0 0 0 0 0]
         [1 0 0 0 0 0 0]
         [0 0 0 0 1 0 0]
         [0 0 0 1 0 0 0]
         [0 0 0 0 0 0 1]
         [0 0 0 0 0 1 0]]

        """

        if sbunch and (start or end):
            raise ValueError('Either sbunch or (start and end) can be specified.')
        elif sbunch:
            for graph in self._get(sbunch=sbunch):
                graph.add_edges_from(ebunch, **attrs)
        else:
            for graph in self._get(start=start, end=end, split_overlaps=True):
                graph.add_edges_from(ebunch, **attrs)

    @staticmethod
    def load_from_txt(path, delimiter=";", comments="#", start='start', end='end'):
        """Read snapshot graph in from path.
           Every line in the file must be an adjacency matrix, with rows separated by delimiter.

        Parameters
        ----------
        path : string or file
           Filename to read.

        comments : string, optional
           Marker for comment lines

        start: string, optional
            Marker for start timestamps

        end: string, optional
            Marker for end timestamps

        delimiter : string, optional
           Separator for rows in matrix.  The default is ;. Cannot be whitespace or \n.

        Returns
        -------
        G: SnapshotGraph
            The graph corresponding to the list of adjacency matrices.

        Examples
        --------
        >>> G=dnx.Snapshotgraph.load_from_txt("my_dygraph.txt")
        """

        if delimiter == ' ' or delimiter == '\n':
            raise ValueError("Delimiter cannot be " + delimiter + ".")

        sg = SnapshotGraph()

        with open(path, 'r') as file:
            for line in file:
                p = line.find(comments)
                if p >= 0:
                    line = line[:p]
                if not len(line):
                    continue

                p = min(line.find(start), line.find(end))
                interval = [None, None]

                for item in line[p:].split():
                    key, value = item.split('=')

                    try:
                        value = float(value)
                    except:
                        raise ValueError('Value of "{}" must be float.'.format(key))

                    if key == start:
                        interval[0] = value
                    else:
                        interval[1] = value

                if interval[0] is None or interval[1] is None:
                    raise ValueError('A snapshot does not include its interval')

                line = line[:p].strip()
                matrix = []
                for row in line.split(delimiter):
                    matrix.append(row.split(' '))

                g = from_numpy_array(np.array(matrix))
                sg.insert(g, start=interval[0], end=interval[1])

        return sg

    def save_to_txt(self, path, delimiter=";", start='start', end='end'):
        """Write snapshot graph to path.
           Every line in the file will be an adjacency matrix.

        Parameters
        ----------
        path : string or file
           Filename to write.

        start: string, optional
            Marker for start timestamps

        end: string, optional
            Marker for end timestamps

        delimiter : string, optional
           Separator for rows in matrix.  The default is ;. Cannot be whitespace or \n.

        Examples
        --------
        >>> G.save_to_txt("my_dygraph.txt")
        """

        if len(self) == 0:
            raise ValueError("Given graph is empty.")

        if delimiter == ' ' or delimiter == '\n':
            raise ValueError("Delimiter cannot be " + delimiter + ".")

        with open(path, 'w') as file:
            for interval, graph in self._get(include_interval=True):
                m = adjacency_matrix(graph).todense()
                line = delimiter.join(' '.join(x for x in y) for y in np.asarray(m, dtype=str)) + ' ' + start + '=' +\
                    str(interval[0]) + ' ' + end + '=' + str(interval[1]) + '\n'

                file.write(line)

    def compute_network_statistic(self, nx_statistic_function, sbunch=None, start=None, end=None, **kwargs):
        """Compute networkx statistics on each snapshot.

        Parameters
        ----------
        nx_statistic_function : function from networkx.algorithms
           Statistic function to calculate.
        sbunch: snapshots indices to compute statistic
        start: start timestamp, inclusive
        end: end timestamp, exclusive
        kwargs : optional
           inputs for nx_statistic_function

        Examples
        --------
        >>> G.compute_network_statistic(nx.algorithms.centrality.degree_centrality)
        """

        if sbunch and (start or end):
            raise ValueError('Either sbunch or (start and end) can be specified.')
        elif sbunch:
            return [nx_statistic_function(graph, **kwargs) for graph in self._get(sbunch=sbunch)]
        else:
            return [nx_statistic_function(graph, **kwargs) for graph in self._get(start=start, end=end)]
