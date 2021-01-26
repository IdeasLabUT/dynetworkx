from networkx.classes.digraph import DiGraph
from networkx.classes.multidigraph import MultiDiGraph
from dynetworkx.classes.snapshotgraph import SnapshotGraph


class SnapshotDiGraph(SnapshotGraph):

    def add_snapshot(self, ebunch=None, graph=None, start=None, end=None, time=None, multi=False):
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
        multi : boolean, optional (default= False)
            Determines if type of graphs in snapshot are DiGraphs for MultiDiGraphs

        Returns
        -------
        None

        Examples
        --------
        >>> G = dnx.SnapshotGraph()
        >>> G.add_snapshot([(1, 4), (1, 3)])
        """
        if not graph:
            if multi is True:
                g = MultiDiGraph()
            else:
                g = DiGraph()
            g.add_edges_from(ebunch)
        else:
            g = graph

        if time is not None and (start or end):
            raise ValueError('Time and (start or end) cannot both be specified.')
        elif time is not None:
            self.insert(g, time=time)
        elif (start is None and end is not None) or (start is not None and end is None):
            raise ValueError('Start and end must both be specified for intervals.')
        else:
            self.insert(g, start=start, end=end)
