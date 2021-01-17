from networkx.classes.digraph import DiGraph
from networkx.classes.multidigraph import MultiDiGraph
from dynetworkx.classes.snapshotgraph import SnapshotGraph
import numpy as np
from networkx import adjacency_matrix, from_numpy_array


class SnapshotDiGraph(SnapshotGraph):

    def add_snapshot(self, ebunch=None, graph=None, num_in_seq=None, multi=False):
        """Add a snapshot with a bunch of edge values.

        Parameters
        ----------

        ebunch : container of edges, optional (default= None)
            Each edge in the ebunch list will be included to all added graphs.
        graph : networkx graph object, optional (default= None)
            networkx graph to be inserted into snapshot graph.
        num_in_seq : integer, optional (default= None)
            Time slot to begin insertion at.
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

        if not num_in_seq:
            num_in_seq = len(self.snapshots)

        if num_in_seq > len(self.snapshots):
            self.insert(g, snap_len=num_in_seq-len(self.snapshots)+1, num_in_seq=num_in_seq)
        else:
            self.insert(g, snap_len=1, num_in_seq=num_in_seq)
