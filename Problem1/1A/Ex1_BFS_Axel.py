from collections import defaultdict, deque
import random as rand
import numpy as np
import tqdm as tqdm
import networkx as nx
import matplotlib.pyplot as plt
import time
from multiprocessing import Pool, cpu_count


class Graph:
    def __init__(self):
        self.graph = defaultdict(list)

    def addEdge(self, u, v):
        self.graph[u].append(v)


    def BFS(self, start):
        bfs_tree = Graph()
        visited = set()
        queue = deque([start])
        visited.add(start)

        while queue:
            u = queue.popleft()
            #print (s, end = " ")
            for v in self.graph[u]:
                if v not in visited:
                    visited.add(v)
                    queue.append(v)
                    bfs_tree.addEdge(u, v)

        return bfs_tree, visited




def visualize_nx_graph(Graph, title, gravity=False):
    plt.figure(figsize=(8, 6))
    
    if gravity:
        pos = nx.bfs_layout(Graph, 0)
    else:
        pos = nx.spring_layout(Graph)

    nx.draw(Graph, pos, with_labels=True,
            node_color='lightblue',
            node_size=500,
            edge_color='gray')

    plt.title(title)
    plt.show(block=False)
    

def nx_to_mygraph(nx_graph):
    g = Graph()
    for u, v in nx_graph.edges():
        g.addEdge(u, v)
    return g

def CreateGraph_AXEL (Nodes: int, edges: int, seed: int, directed: bool):
    graph = Graph()
    graph = nx.gnm_random_graph(Nodes, edges, seed, directed=directed)
    return graph

def run_test(Graf: Graph):
    t_0 = time.perf_counter_ns()
    BFS_TREE = Graf.BFS(0)
    t_1 = time.perf_counter_ns()
    #visualizeGraph(BFS_TREE,"Jeg er et træ", True)

    return t_1 - t_0



def sequintelTest():
    Nodes = [10, 100, 1000, 10000, 100000, 1000000]
    Edges_prNode = [Nodes[0]*6, Nodes[1]*6, Nodes[2]*6, Nodes[3]*6, Nodes[4]*6, Nodes[5]*6]
    runs = 32

    
    for (num_nodes, num_edges) in zip(Nodes, Edges_prNode):
        t_perf = np.zeros(runs)

        for i in tqdm.tqdm(range(runs)):
            nx_Graf = CreateGraph_AXEL(num_nodes, num_edges, i, False)
            #visualize_nx_graph(nx_Graf,"Kludder kage", False)
            Graf = nx_to_mygraph(nx_Graf)
            t_perf[i] = run_test(Graf) /1000 # Omregn til mikrosekunder
            
        print(f"Det tog {t_perf.mean():0.1f} us, std: {t_perf.std():0.1f} us")


        

if __name__ == "__main__":
       
    #plt.show()
    sequintelTest()        # Lavet til det sequintielle .
    