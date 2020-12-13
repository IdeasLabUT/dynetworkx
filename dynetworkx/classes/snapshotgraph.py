from networkx.classes.graph import Graph
import numpy as np
from networkx import adjacency_matrix, from_numpy_array
from sortedcontainers import SortedDict, SortedList

NEG_INF = float(-10000000000)
POS_INF = float(10000000000)


class SnapshotGraph(object):
    def __init__(self, **attr):
        self.graph = {}
        self.graph.update(attr)
        self.snapshots = SortedDict()

    @property
    def name(self):
        """String identifier of the interval graph.

        This interval graph attribute appears in the attribute dict SnapshotGraph.graph
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

    def insert(self, graph, start, end):
        """Insert a graph into the snapshot graph, with specified intervals.

        Parameters
        ----------
        graph: networkx graph object
            A networkx graph to be inserted into snapshot graph.
        start: start of the interval, inclusive
        end: end of the interval, exclusive

        Returns
        -------
        None

        Examples
        --------
        >>> nxG1 = nx.Graph()
        >>> nxG1.add_edges_from([(1, 2), (1, 3)])
        >>> G = dnx.SnapshotGraph()
        >>> G.insert(nxG1, 0, 3)

        """
        if start > end:
            raise ValueError('Start of the interval must be lower or equal to end')
        else:
            self.snapshots.update({(start, end): graph})

    def add_snapshot(self, ebunch=None, graph=None, start=None, end=None):
        """Add a snapshot with a bunch of edge values.

        Parameters
        ----------
        ebunch : container of edges, optional (default= None)
            Each edge in the ebunch list will be included to all added graphs.
        graph : networkx graph object, optional (default= None)
            networkx graph to be inserted into snapshot graph.
        num_in_seq : integer, optional (default= None)
            Time slot to begin insertion at.

        Returns
        -------
        None

        Examples
        --------
        >>> G = dnx.SnapshotGraph()
        >>> G.add_snapshot([(1, 4), (1, 3)])
        """
        if not graph:
            g = Graph()
            g.add_edges_from(ebunch)
        else:
            g = graph

        if start is None or end is None:
            raise ValueError('Start and end must both be specified.')
        else:
            self.insert(g, start, end)

    def subgraph(self, nbunch, sbunch=None, start=None, end=None): # TODO: have not finished
        """Return a snapshot graph containing only the nodes in bunch, and snapshot indexes in sbunch.

        Parameters
        ----------
        nbunch : container of nodes
            Each node in the nbunch list will be included in all subgraphs indexed in sbunch.
        sbunch : container of edges, optional (default= None)
            Each snapshot index in this list will be included in the returned list
            of subgraphs. It is highly recommended that this list is sequential,
            however it can be out of order.

        Returns
        -------
            snap_graph : SnapshotGraph object
                Contains only the nodes in bunch, and snapshot indexes in sbunch.

        Examples
        --------
        >>> G = dnx.SnapshotGraph()
        >>> G.add_snapshot([(1, 2), (2, 3), (4, 6), (2, 4)])
        >>> G.add_snapshot([(1, 2), (2, 3), (4, 6), (2, 4)])
        >>> H = G.subgraph([4, 6])
        >>> type(H)
        <class 'snapshotgraph.SnapshotGraph'>
        >>> list(H.get([0])[0].edges(data=True))
        [(4, 6, {})]
        """

        if sbunch and (start or end):
            raise ValueError('Either sbunch or (start and end) can be specified.')
        elif sbunch:
            graph_list = self.get(sbunch=sbunch)
        else:
            graph_list = self.get(start=start, end=end)
        subgraph = SnapshotGraph()

        for snapshot in graph_list:
            subgraph.add_snapshot(graph=snapshot.subgraph(nbunch))
        subgraph.graph = self.graph

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
        weight : string, optional (default= None)
            The edge attribute that holds the numerical value used as a weight. If None, then each edge has weight 1. The degree is the sum of the edge weights adjacent to the node.

        Returns
        -------
            degree_list : list
                List of DegreeView objects containing the degree of each node, indexed by requested snapshot.

        Examples
        --------
        >>> G = dnx.SnapshotGraph()
        >>> G.add_snapshot([(1, 2), (1, 3)])
        >>> G.add_snapshot([(1, 4), (1, 3)])
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
            graph_list = self.get(sbunch=sbunch)
        else:
            graph_list = self.get(start=start, end=end)

        return_degrees = []

        if nbunch:
            for g in graph_list:
                return_degrees.append(g.degree(nbunch, weight=weight))
        else:
            for g in graph_list:
                return_degrees.append(g.degree(g, weight=weight))

        return return_degrees

    def number_of_nodes(self, sbunch=None, start=None, end=None):
        """Gets number of nodes in each snapshot requested in 'sbunch'.

        Parameters
        ----------
        sbunch : container of snapshot indexes, optional (default= None)
            Each snapshot index in this list will be included in the returned list
            of number of nodes in the snapshot. It is highly recommended that this list is sequential,
            however it can be out of order.

        Returns
        -------
            num_nodes : list
                A list of of the number of nodes in each requested snapshot.

        Examples
        --------
        >>> G = dnx.SnapshotGraph()
        >>> G.add_snapshot([(1, 2), (1, 3)])
        >>> G.add_snapshot([(1, 4), (1, 3)])
        >>> G.number_of_nodes(sbunch=[1])
        [3]
        >>> G.number_of_nodes(sbunch=[0, 1])
        [3, 3]
        """
        # returns a list of the number of nodes in each graph in the range

        if sbunch and (start or end):
            raise ValueError('Either sbunch or (start and end) can be specified.')
        elif sbunch:
            graph_list = self.get(sbunch=sbunch)
        else:
            graph_list = self.get(start=start, end=end)

        return [g.number_of_nodes() for g in graph_list]

    def order(self, sbunch=None, start=None, end=None):
        """Returns order of each graph requested in 'sbunch'.

        Parameters
        ----------
        sbunch : container of snapshot indexes, optional (default= None)
            Each snapshot index in this list will be included in the returned list
            of node orders. It is highly recommended that this list is sequential,
            however it can be out of order.

        Returns
        -------
            snapshot_orders : list
                A list of the orders of each snapshot.

        Examples
        --------
        >>> G = dnx.SnapshotGraph()
        >>> G.add_snapshot([(1, 2), (1, 3)])
        >>> G.add_snapshot([(1, 4), (1, 3)])
        >>> G.order(sbunch=[1])
        [3]
        >>> G.order(sbunch=[0, 1])
        [3, 3]
        """
        # returns a list of the order of the graph in the range

        if sbunch and (start or end):
            raise ValueError('Either sbunch or (start and end) can be specified.')
        elif sbunch:
            graph_list = self.get(sbunch=sbunch)
        else:
            graph_list = self.get(start=start, end=end)

        return [g.order() for g in graph_list]

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

        Returns
        -------
            List of boolean values if index in sbunch contains n.

        Examples
        --------
        >>> G = dnx.SnapshotGraph()
        >>> G.add_snapshot([(1, 2), (1, 3)])
        >>> G.add_snapshot([(1, 4), (1, 3)])
        >>> G.has_node(1, sbunch=[1])
        [True]
        >>> G.has_node(1)
        [True, True]

        """

        if sbunch and (start or end):
            raise ValueError('Either sbunch or (start and end) can be specified.')
        elif sbunch:
            graph_list = self.get(sbunch=sbunch)
        else:
            graph_list = self.get(start=start, end=end)

        return [g.has_node(n) for g in graph_list]

    def is_multigraph(self, sbunch=None, start=None, end=None):
        """Returns a list of boolean values for if the graph at the index is a multigraph.

        Parameters
        ----------
        sbunch : container of snapshot indexes, optional (default= None)
            Each snapshot index in this list will be included in the returned list
            of booleans. It is highly recommended that this list is sequential,
            however it can be out of order.

        Returns
        -------
            mutli_list : list
                List of boolean values if index in sbunch is a multigraph.

        Examples
        --------
        >>> G = dnx.SnapshotGraph()
        >>> G.add_snapshot([(1, 2), (1, 3)])
        >>> G.add_snapshot([(1, 4), (1, 3)])
        >>> G.is_multigraph(sbunch=[0, 1])
        [False, False]
        >>> G.is_multigraph()
        [False, False]

        """

        if sbunch and (start or end):
            raise ValueError('Either sbunch or (start and end) can be specified.')
        elif sbunch:
            graph_list = self.get(sbunch=sbunch)
        else:
            graph_list = self.get(start=start, end=end)

        return [g.is_multigraph() for g in graph_list]

    def is_directed(self, sbunch=None, start=None, end=None):
        """Returns a list of boolean values for if the graph at the index is a directed graph.

        Parameters
        ----------
        sbunch : container of snapshot indexes, optional (default= None)
            Each snapshot index in this list will be included in the returned list
            of booleans. It is highly recommended that this list is sequential,
            however it can be out of order.

        Returns
        -------
            is_direct_list : list
                List of boolean values if index in sbunch is a directed graph.

        Examples
        --------
        >>> G = dnx.SnapshotGraph()
        >>> G.add_snapshot([(1, 2), (1, 3)])
        >>> G.add_snapshot([(1, 4), (1, 3)])
        >>> G.is_directed(sbunch=[0, 1])
        [False, False]
        >>> G.is_directed()
        [False, False]

        """

        if sbunch and (start or end):
            raise ValueError('Either sbunch or (start and end) can be specified.')
        elif sbunch:
            graph_list = self.get(sbunch=sbunch)
        else:
            graph_list = self.get(start=start, end=end)

        return [g.is_directed() for g in graph_list]

    def to_directed(self, sbunch=None, start=None, end=None):
        """Returns a list of networkx directed graph objects.

        Parameters
        ----------
        sbunch : container of snapshot indexes, optional (default= None)
            Each snapshot index in this list will be included in the returned list
            of directed graphs. It is highly recommended that this list is sequential,
            however it can be out of order.

        Returns
        -------
            direct_list : list
                List of networkx directed graph objects.

        Examples
        --------
        >>> G = dnx.SnapshotGraph()
        >>> G.add_snapshot([(1, 2), (1, 3)])
        >>> G.add_snapshot([(1, 4), (1, 3)])
        >>> G.to_directed(sbunch=[0, 1])
        [<networkx.classes.digraph.DiGraph object at 0x7f1a6de49dd8>, <networkx.classes.digraph.DiGraph object at 0x7f1a6de49e10>]

        """

        if sbunch and (start or end):
            raise ValueError('Either sbunch or (start and end) can be specified.')
        elif sbunch:
            graph_list = self.get(sbunch=sbunch)
        else:
            graph_list = self.get(start=start, end=end)

        return [g.to_directed() for g in graph_list]

    def to_undirected(self, sbunch=None, start=None, end=None, ):
        """Returns a list of networkx graph objects.

        Parameters
        ----------
        sbunch : container of snapshot indexes, optional (default= None)
            Each snapshot index in this list will be included in the returned list
            of undirected graphs. It is highly recommended that this list is sequential,
            however it can be out of order.

        Returns
        -------
            undirect_list : list
                List of networkx graph objects.

        Examples
        --------
        >>> G = dnx.SnapshotGraph()
        >>> G.add_snapshot([(1, 2), (1, 3)])
        >>> G.add_snapshot([(1, 4), (1, 3)])
        >>> G.to_directed(sbunch=[0, 1])
        [<networkx.classes.graph.Graph object at 0x7ff532219e10>, <networkx.classes.graph.Graph object at 0x7ff532219e48>]

        """

        if sbunch and (start or end):
            raise ValueError('Either sbunch or (start and end) can be specified.')
        elif sbunch:
            graph_list = self.get(sbunch=sbunch)
        else:
            graph_list = self.get(start=start, end=end)

        return [g.to_undirected() for g in graph_list]

    def size(self, sbunch=None, start=None, end=None, weight=None):
        """Returns the size of each graph index as specified in sbunch as a list.

        Parameters
        ----------
        sbunch : container of snapshot indexes, optional (default= None)
            Each snapshot index in this list will be included in the returned list
            of sizes. It is highly recommended that this list is sequential,
            however it can be out of order.
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
        >>> G.add_snapshot([(1, 2), (1, 3)])
        >>> G.add_snapshot([(1, 4), (1, 3)])
        >>> G.size(sbunch=[0, 1])
        [2, 2]
        >>> G.size()
        [2, 2]

        """

        if sbunch and (start or end):
            raise ValueError('Either sbunch or (start and end) can be specified.')
        elif sbunch:
            graph_list = self.get(sbunch=sbunch)
        else:
            graph_list = self.get(start=start, end=end)

        return [g.size(weight=weight) for g in graph_list]

    def get(self, sbunch=None, start=None, end=None):  # TODO: add examples
        """Returns a list of graphs specified in sbunch.

        Parameters
        ----------
        sbunch : container of snapshot indexes, optional (default= None)
            Each snapshot index in this list will be included in the returned list
            of graphs. It is highly recommended that this list is sequential,
            however it can be out of order.
        start: start timestamp
        end: end timestamp

        Returns
        -------
        List of networkx graph objects.


        Examples
        --------
        >>> G = dnx.SnapshotGraph()
        >>> G.add_snapshot([(1, 2), (1, 3)])
        >>> G.add_snapshot([(1, 4), (1, 3)])
        >>> G.get(sbunch=[0])
        [<networkx.classes.graph.Graph object at 0x7f27f5bd39b0>]
        >>> G.get()
        [<networkx.classes.graph.Graph object at 0x7f27f5bd39b0>, <networkx.classes.graph.Graph object at 0x7f27f5bd3d30>]
        """
        graphs = self.snapshots.values()

        if sbunch and (start or end):
            raise ValueError('Either sbunch or (start and end) can be specified.')
        elif sbunch:  # if retrieve by indexes
            return [graphs[index] for index in sbunch]
        else:  # if retrieve by interval
            if start is None:
                min_idx = 0
            else:
                min_idx = self.snapshots.bisect_left((start,))

                # Decrease 1 index if start is in the middle of an interval
                # Eg: if Keys = [(2,5)(5,6)], start=3 won't retrieve (2,5) as we want,
                # therefore, decrease 1 index to include (2,5). If start=5, then we won't need to change
                if min_idx > 0 and start < self.snapshots.keys()[min_idx][0]:
                    min_idx -= 1

                if min_idx == len(self.snapshots):
                    return iter(())

            if end is None:
                max_idx = len(self.snapshots)
            else:
                max_idx = self.snapshots.bisect_left((end,))

            return graphs[min_idx: max_idx]

    def add_nodes_from(self, nbunch, sbunch=None, start=None, end=None, **attrs):
        """Adds nodes to snapshots in sbunch.

        Parameters
        ----------
        nbunch : container of nodes
            Each node in the nbunch list will be added to all graphs indexed in sbunch.
        sbunch : container of snapshot indexes, optional (default= None)
            Each snapshot index in this list will be included in the returned list
            of node degrees. It is highly recommended that this list is sequential,
            however it can be out of order.

        Returns
        -------
        None

        Examples
        --------
        >>> G = dnx.SnapshotGraph()
        >>> G.add_snapshot([(1, 2), (1, 3)])
        >>> G.add_snapshot([(1, 4), (1, 3)])

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
            graph_list = self.get(sbunch=sbunch)
        else:
            graph_list = self.get(start=start, end=end)

        for g in graph_list:
            g.add_nodes_from(nbunch, **attrs)

    def add_edges_from(self, ebunch, sbunch=None, start=None, end=None, **attrs):
        """Adds edges to snapshots in sbunch.

        Parameters
        ----------
        ebunch : container of edges
            Each edge in the ebunch list will be added to all graphs indexed in sbunch.
        sbunch : container of snapshot indexes, optional (default= None)
            Each snapshot index in this list will be included in the returned list
            of node degrees. It is highly recommended that this list is sequential,
            however it can be out of order.

        Returns
        -------
        None

        Examples
        --------
        >>> G = dnx.SnapshotGraph()
        >>> G.add_snapshot([(1, 2), (1, 3)])
        >>> G.add_snapshot([(1, 4), (1, 3)])

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
            graph_list = self.get(sbunch=sbunch)
        else:
            graph_list = self.get(start=start, end=end)

        for g in graph_list:
            g.add_edges_from(ebunch, **attrs)

    @staticmethod
    def load_from_txt(path, delimiter=";", comments="#"):
        """Read snapshot graph in from path.
           Every line in the file must be an adjacency matrix, with rows separated by delimiter.

        Parameters
        ----------
        path : string or file
           Filename to read.

        comments : string, optional
           Marker for comment lines

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
                line = line.strip()
                matrix = []
                for row in line.split(delimiter):
                    matrix.append(row.split(' '))

                g = from_numpy_array(np.array(matrix))
                sg.insert(g)

        return sg

    def save_to_txt(self, path, delimiter=";"):
        """Write snapshot graph to path.
           Every line in the file will be an adjacency matrix.

        Parameters
        ----------
        path : string or file
           Filename to write.

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

        nodelist = set()
        with open(path, 'w') as file:

            for graph in self.get():
                for node in graph.nodes():
                    nodelist.add(node)

            for graph in self.get():
                for node in nodelist:
                    if node not in graph.nodes():
                        graph.add_node(node)
                m = adjacency_matrix(graph).todense()
                line = delimiter.join(' '.join(x for x in y) for y in np.asarray(m, dtype=str)) + '\n'

                file.write(line)

    def compute_network_statistic(self, nx_statistic_function, start=None, end=None, **kwargs):
        """Compute networkx statistics on each snapshot.

        Parameters
        ----------
        nx_statistic_function : function from networkx.algorithms
           Statistic function to calculate.

        begin : int, optional (default= None)
           Number of snapshot to begin calculation

        end : int, optional (default= None)
           Number of snapshot to end calculation

        kwargs : optional
           inputs for nx_statistic_function

        Examples
        --------
        >>> G.compute_network_statistic(nx.algorithms.centrality.degree_centrality)
        """

        # if sbunch and (start or end):
        #     raise ValueError('Either sbunch or (start and end) can be specified.')
        # elif sbunch:
        #     graph_list = self.get(sbunch=sbunch)
        # else:
        #     graph_list = self.get(start=start, end=end)

        output = []
        for graph in self.snapshots.values()[start:end]:
            output.append(nx_statistic_function(graph, **kwargs))
        return output

    def get_missing_intervals(self):
        pass
