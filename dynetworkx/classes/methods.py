from impulsegraph import ImpulseGraph
from sortedcontainers import SortedSet, SortedDict

graph = ImpulseGraph()
graph.add_edge(1,2,10)
graph.add_edge(2,3,11)
graph.add_edge(3,4,12)
graph.add_edge(1,3,13)

def shortest_path(graph,u,v,time=float('-inf'),time_dependent=True,heuristic=None,visited_nodes=None,unchecked_nodes=None,possible_paths=None):
    #print('U:',u)
    if visited_nodes is None:
        visited_nodes = set()
    if possible_paths is None:
        possible_paths = {u:SortedDict()}
    if unchecked_nodes is None:
        unchecked_nodes = SortedSet([u],key=lambda k: len(possible_paths[k])) #set of unchecked nodes sorted by length of path

    for edge in graph.edges(u):
        #print(edge)
        if edge[0] in visited_nodes or edge[1] in visited_nodes:    #node already been visited, skip
            continue
         
        if edge[1] not in unchecked_nodes:  #discovered new node, add to sets
            if time_dependent:
                if edge[2] >= time:
                    possible_paths[edge[1]] = possible_paths[u].setdefault(edge[2],[]) + [edge]
                    unchecked_nodes.add(edge[1])
                    
                else:
                    possible_paths[edge[1]] = possible_paths[u][edge[2]] + [edge]
                    unchecked_nodes.add(edge[1])      
                
        else:   #rediscovered a node, check to see if time is new, if time rediscovered, check to see if new path is shorter
            if time_dependent:
                if edge[2] >= time:
                    if len(possible_paths[edge[1]]) > len(possible_paths[edge[0]][edge[2]])+1:
                        possible_paths[edge[1]] = possible_paths[u][edge[2]] + [edge]
            else:
                if len(possible_paths[edge[1]]) > len(possible_paths[edge[0]][edge[2]])+1:
                    possible_paths[edge[1]] = possible_paths[u][edge[2]] + [edge]
                    
    visited_nodes.add(u)
    print(u,list(unchecked_nodes),u in unchecked_nodes)
    unchecked_nodes.remove(u)

    #check if v has been found
    if v in visited_nodes:
        return possible_paths[v]

    #check if ran out of options
    if len(unchecked_nodes) == 0:
        return []

    print(visited_nodes,possible_paths)
    
    return shortest_path(graph,unchecked_nodes[0],v,time=possible_paths[unchecked_nodes[0]][-1][2],
                         time_dependent=time_dependent,heuristic=heuristic,visited_nodes=visited_nodes,unchecked_nodes=unchecked_nodes,possible_paths=possible_paths)
    
f = shortest_path(graph,1,4)
