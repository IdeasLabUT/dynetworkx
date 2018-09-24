from __future__ import print_function
'''
    File Name: dyn_edgelist.py
    Author: Brian O'Leary
    Date Created: 2017-06-20
    Date Last Modified:
'''
import networkx as nx
from dynetworkx.classes.dynamicgraph import DynamicGraph
from dynetworkx.classes.helpers import timer
import csv
from datetime import datetime
import time

def read_edgelist(filename):
    G = DynamicGraph()
    with open(filename, 'r') as r:
        # operating under the assumption that there is a triplet
        # with all integers
        for line in r.readlines():
            items = line.strip().split(',')
            u = int(items[0])
            v = int(items[1])
            start_time = int(items[2])
            if len(items) == 3:
                end_time = start_time
            else:
                end_time = items[3]

            G.add_edge(u, v, start_time, end_time)
    return G

@timer
def read_triplet_timestamp(filename):
    G = DynamicGraph()
    with open(filename, 'r') as r:
        reader = csv.reader(r, delimiter=',', quotechar='"')
        for row in reader:
            u = row[0]
            v = row[1]
            t = datetime.strptime(row[2], '%Y-%m-%d %H:%M:%S')
            unix_time = time.mktime(t.timetuple())
            G.add_edge(u, v, unix_time, unix_time)
    return G


if __name__ == '__main__':
    #G = read_edgelist('../../datasets/RealityMiningCallSmsDataUnsorted.csv')
    G = read_triplet_timestamp('../../datasets/hurricaneSandy2012-exported-2017-08-22.csv')
    G.edge_count_filter(10)
