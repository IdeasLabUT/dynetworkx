from networkx.classes.graph import Graph


class SnapshotGraph(object):
    def __init__(self, **attr):
        self.graph = {}
        self.graph.update(attr)
        self.snapshots = []

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
        Number graphs in snapshot graph
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
        >>> G.insert(nxG1)
        >>> G.insert(nxG2)
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
        >>> G.insert(nxG1)
        >>> G.insert(nxG2)
        >>> nxG1 in G
        True
        """

        try:
            return graph in self.snapshots
        except TypeError:
            return False

    def insert(self, graph, snap_len=None, num_in_seq=None):
        """Insert a graph into the snapshot graph, with options for inserting at a given index, with some snapshot length.

        Parameters
        ----------
        graph: networkx graph object
            networkx graph to be inserted into snapshot graph.
        snap_len: Integer
            Length of the snapshot.
        num_in_seq: Integer
            Time slot to begin insertion at.


        Returns
        -------
        None

        Examples
        --------
        >>> nxG1 = nx.Graph()
        >>>
        >>> nxG1.add_edges_from([(1, 2), (1, 3)])
        >>>
        >>> G = dnx.SnapshotGraph()
        >>> G.insert(nxG1)
        """
        for _ in range(snap_len):
            self.snapshots.insert(num_in_seq, graph)

    def add_snapshot(self, ebunch=None, graph=None, num_in_seq=None):
        """Add a snapshot with a bunch of edge values.

        Parameters
        ----------
        ebunch : List of desired edges to add
            Each edge in the ebunch list will be included to all added graphs.
        graph: networkx graph object
            networkx graph to be inserted into snapshot graph.
        num_in_seq: Integer
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

        if (not num_in_seq) or (num_in_seq == len(self.snapshots) + 1):
            self.snapshots.append(g)

        elif num_in_seq > len(self.snapshots):
            while num_in_seq > len(self.snapshots):
                self.snapshots.append(g)
        else:
            self.insert(g, snap_len=1, num_in_seq=num_in_seq)

    def subgraph(self, nbunch=None, sbunch=None):
        """Return a snapshot graph containing only the nodes in bunch, and snapshot indexes in sbunch.

        Parameters
        ----------
        sbunch : List of indexes for desired snapshots
            Each snapshot index in this list will be included in the returned list
            of subgraphs. It is highly recommended that this list is sequential,
            however it can be out of order.
        nbunch : List of desired nodes to add
            Each node in the nbunch list will be included in all subgraphs indexed in sbunch.

        Returns
        -------
            SnapshotGraph
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

        if sbunch:
            if len(sbunch) != len(nbunch):
                raise ValueError(
                    'node list({}) must be equal in length to number of desired snapshots({})'.format(len(nbunch),
                                                                                                      len(sbunch)))
            min_index = min(sbunch)
            max_index = max(sbunch)
        else:
            min_index = 0
            max_index = len(self.snapshots)

        graph_list = self.snapshots[min_index:max_index+1]
        # only get the indexes wanted
        if sbunch:
            graph_list = [graph_list[index - min_index] for index in sbunch]

        subgraph = SnapshotGraph()

        for snapshot in graph_list:
            subgraph.add_snapshot(graph=snapshot.subgraph(nbunch))
        subgraph.graph = self.graph

        return subgraph

    def degree(self, sbunch=None, nbunch=None, weight=None):
        """Return a list of tuples containing the degrees of each node in each snapshot

        Parameters
        ----------
        sbunch : List of indexes for desired snapshots
            Each snapshot index in this list will be included in the returned list
            of node degrees. It is highly recommended that this list is sequential,
            however it can be out of order.

        nbunch : List of desired nodes
            Each node in the nbunch list will be included in the returned list of
            node degrees.

        Returns
        -------
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
        if sbunch:
            min_index = min(sbunch)
            max_index = max(sbunch)
        else:
            min_index = 0
            max_index = len(self.snapshots)

        # get all indexes between min and max
        graph_list = self.snapshots[min_index:(max_index+1)]
        # only get the indexes wanted
        if sbunch:
            graph_list = [graph_list[index - min_index] for index in sbunch]

        return_degrees = []

        for g in graph_list:
            return_degrees.append(g.degree(nbunch, weight=weight))

        return return_degrees

    def number_of_nodes(self, sbunch=None):
        """
        Gets number of nodes in each snapshot requested in 'sbunch'.

        Parameters
        ----------
        sbunch : List of indexes for desired snapshots
            Each snapshot index in this list will be included in the returned list
            of number of nodes in the snapshot. It is highly recommended that this list is sequential,
            however it can be out of order.

        Returns
        -------
            A list of of the number of nodes in each requested snapshot.

        Examples
        --------
        """
        # returns a list of the number of nodes in each graph in the range
        if sbunch:
            min_index = min(sbunch)
            max_index = max(sbunch)
        else:
            min_index = 0
            max_index = len(self.snapshots)
        # get all indexes between min and max
        graph_list = self.snapshots[min_index:max_index+1]
        # only get the indexes wanted
        graph_list = [graph_list[index - min_index] for index in sbunch]

        return [g.number_of_nodes() for g in graph_list]

    def order(self, sbunch=None):
        """
        Gets order of each graph requested in 'sbunch'.

        Parameters
        ----------
        sbunch : List of indexes for desired snapshots
            Each snapshot index in this list will be included in the returned list
            of node orders. It is highly recommended that this list is sequential,
            however it can be out of order.

        Returns
        -------
            A list of the orders of each snapshot

        Examples
        --------

        """
        # returns a list of the order of the graph in the range
        if sbunch:
            min_index = min(sbunch)
            max_index = max(sbunch)
        else:
            min_index = 0
            max_index = len(self.snapshots)
        # get all indexes between min and max
        graph_list = self.snapshots[min_index:max_index+1]
        # only get the indexes wanted
        graph_list = [graph_list[index - min_index] for index in sbunch]

        return [g.order() for g in graph_list]

    def has_node(self, n, sbunch=None):
        """
        Gets boolean list of if a snapshot in 'sbunch' contains node 'n'.

        Parameters
        ----------
        n: networkx node object
            node to be checked for in requested snapshots

        sbunch : List of indexes for desired snapshots
            Each snapshot index in this list will be included in the returned list
            of if the snapshot graph includes the node. It is highly recommended
            that this list is sequential, however it can be out of order.

        Returns
        -------

        Examples
        --------
        """
        # returns a list of the order of the graph in the range
        if sbunch:
            min_index = min(sbunch)
            max_index = max(sbunch)
        else:
            min_index = 0
            max_index = len(self.snapshots)
        # get all indexes between min and max
        graph_list = self.snapshots[min_index:max_index+1]
        # only get the indexes wanted
        graph_list = [graph_list[index - min_index] for index in sbunch]

        return [g.has_node(n) for g in graph_list]

    def is_multigraph(self, sbunch=None):
        """

        Parameters
        ----------
        sbunch : List of indexes for desired snapshots
            Each snapshot index in this list will be included in the returned list
            of booleans. It is highly recommended that this list is sequential,
            however it can be out of order.

        Returns
        -------

        Examples
        --------

        """
        # returns a list of the order of the graph in the range
        if sbunch:
            min_index = min(sbunch)
            max_index = max(sbunch)
        else:
            min_index = 0
            max_index = len(self.snapshots)
        # get all indexes between min and max
        graph_list = self.snapshots[min_index:max_index+1]
        # only get the indexes wanted
        graph_list = [graph_list[index - min_index] for index in sbunch]

        return [g.is_multigraph() for g in graph_list]

    def is_directed(self, sbunch=None):
        """

        Parameters
        ----------
        sbunch : List of indexes for desired snapshots
            Each snapshot index in this list will be included in the returned list
            of booleans. It is highly recommended that this list is sequential,
            however it can be out of order.

        Returns
        -------


        Examples
        --------
        """
        # returns a list of the order of the graph in the range
        if sbunch:
            min_index = min(sbunch)
            max_index = max(sbunch)
        else:
            min_index = 0
            max_index = len(self.snapshots)
        # get all indexes between min and max
        graph_list = self.snapshots[min_index:max_index+1]
        # only get the indexes wanted
        graph_list = [graph_list[index - min_index] for index in sbunch]

        return [g.is_directed() for g in graph_list]

    def to_directed(self, sbunch=None):
        """

        Parameters
        ----------
        sbunch : List of indexes for desired snapshots
            Each snapshot index in this list will be included in the returned list
            of directed graphs. It is highly recommended that this list is sequential,
            however it can be out of order.

        Returns
        -------


        Examples
        --------
        """
        # returns a list of the order of the graph in the range
        if sbunch:
            min_index = min(sbunch)
            max_index = max(sbunch)
        else:
            min_index = 0
            max_index = len(self.snapshots)
        # get all indexes between min and max
        graph_list = self.snapshots[min_index:max_index+1]
        # only get the indexes wanted
        graph_list = [graph_list[index - min_index] for index in sbunch]

        return [g.to_directed() for g in graph_list]

    def to_undirected(self, sbunch=None):
        """

        Parameters
        ----------
        sbunch : List of indexes for desired snapshots
            Each snapshot index in this list will be included in the returned list
            of undirected graphs. It is highly recommended that this list is sequential,
            however it can be out of order.

        Returns
        -------

        Examples
        --------

        """
        # returns a list of the order of the graph in the range
        if sbunch:
            min_index = min(sbunch)
            max_index = max(sbunch)
        else:
            min_index = 0
            max_index = len(self.snapshots)
        # get all indexes between min and max
        graph_list = self.snapshots[min_index:max_index+1]
        # only get the indexes wanted
        graph_list = [graph_list[index - min_index] for index in sbunch]

        return [g.to_undirected() for g in graph_list]

    def size(self, sbunch=None, weight=None):
        """
        Returns the size of each graph index as specified in sbunch as a list.

        Parameters
        ----------
        sbunch : List of indexes for desired snapshots
            Each snapshot index in this list will be included in the returned list
            of sizes. It is highly recommended that this list is sequential,
            however it can be out of order.

        Parameters
        ----------
        weight

        Returns
        -------
        List of

        Examples
        --------

        """
        # returns a list of the order of the graph in the range
        if sbunch:
            min_index = min(sbunch)
            max_index = max(sbunch)
        else:
            min_index = 0
            max_index = len(self.snapshots)
        # get all indexes between min and max
        graph_list = self.snapshots[min_index:max_index+1]
        # only get the indexes wanted
        graph_list = [graph_list[index - min_index] for index in sbunch]

        return [g.size(weight=weight) for g in graph_list]

    def get(self, sbunch=None):
        """
        Gets all graphs in snapshot graph specified in sbunch.

        Parameters
        ----------
        sbunch : List of indexes for desired snapshots
            Each snapshot index in this list will be included in the returned list
            of graphs. It is highly recommended that this list is sequential,
            however it can be out of order.

        Returns
        -------
            List of nx.graph objects.

        Examples
        --------

        """
        if sbunch:
            min_index = min(sbunch)
            max_index = max(sbunch)
        else:
            min_index = 0
            max_index = len(self.snapshots)
        # get all indexes between min and max
        graph_list = self.snapshots[min_index:max_index+1]
        # only get the indexes wanted
        graph_list = [graph_list[index - min_index] for index in sbunch]
        return graph_list

    def add_nodes_from(self, sbunch=None, nbunch=None, **attrs):
        """
        Return a list of tuples containing the degrees of each node in each snapshot

        Parameters
        ----------
        sbunch : List of indexes for desired snapshots
            Each snapshot index in this list will be included in the returned list
            of node degrees. It is highly recommended that this list is sequential,
            however it can be out of order.
        nbunch : List of desired nodes to add
            Each node in the nbunch list will be added to all graphs indexed in sbunch

        Returns
        -------
            List of tuples containing the degrees of each node in each snapshot

        Examples
        --------
        """
        if sbunch:
            min_index = min(sbunch)
            max_index = max(sbunch)
        else:
            min_index = 0
            max_index = len(self.snapshots)
        # get all indexes between min and max
        graph_list = self.snapshots[min_index:max_index+1]
        # only get the indexes wanted
        graph_list = [graph_list[index - min_index] for index in sbunch]

        for g in graph_list:
                g.add_nodes_from(nbunch, **attrs)

    def add_edges_from(self, sbunch=None, ebunch=None, **attrs):
        """
        Return a list of tuples containing the degrees of each node in each snapshot

        Parameters
        ----------
        sbunch : List of indexes for desired snapshots
            Each snapshot index in this list will be included in the returned list
            of node degrees. It is highly recommended that this list is sequential,
            however it can be out of order.
        ebunch : List of desired edges to add
            Each edge in the ebunch list will be added to all graphs indexed in sbunch

        Returns
        -------
            List of tuples containing the degrees of each node in each snapshot

        Examples
        --------
        """
        if sbunch:
            min_index = min(sbunch)
            max_index = max(sbunch)
        else:
            min_index = 0
            max_index = len(self.snapshots)
        # get all indexes between min and max
        graph_list = self.snapshots[min_index:max_index+1]
        # only get the indexes wanted
        graph_list = [graph_list[index - min_index] for index in sbunch]

        for g in graph_list:
                g.add_edges_from(ebunch, **attrs)

