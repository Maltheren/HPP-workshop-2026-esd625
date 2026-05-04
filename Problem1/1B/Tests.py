# Nyeste Version af BFS Mulitprocessing script UDEN Chatteb
import multiprocessing as mp
from collections import defaultdict, deque
import random as rand
import numpy as np
import tqdm as tqdm
import networkx as nx
import matplotlib.pyplot as plt
import time

num_processes = 5






class Graph:

    def CreateGraph (num_nodes: int, max_edges_pr_node: int):
        graph = nx.Graph()
        Nodes = []
        for i in range(num_nodes):
            Nodes.append(i)
        for i in Nodes:
            graph.add_node(Nodes[i], visited=False, Layer=0)
            node_edges = np.random.randint(1, max_edges_pr_node)
            tries = 0
            while node_edges > 0:
                dest_node = np.random.randint(0, num_nodes-1)
                if dest_node != i: 
                    graph.add_edge(i, dest_node)
                    node_edges -= 1
                tries += 1
                if tries > max_edges_pr_node*2:
                    break
        return graph
    
    def mult_init(graph: nx.Graph, start: int, threads: int):
        start_points = []
        neighbours = list(graph.adj[start])
        if threads < len(neighbours):
            for i in range(threads):
                start_points.append(neighbours[i])
        else:
            for i in range(len(neighbours)):
                start_points.append(neighbours[i])

        return start_points
    
    def BFS_Threading(self, start, threads):
        bfs_tree = Graph()
        visited = set()
        visited.add(start)
        current_level = [start]
        
        def process_node(u): 
            local_next = []
            for v in self.graph[u]:
                if v not in visited:
                    visited.add(v)
                    bfs_tree.addEdge(u, v)
                    local_next.append(v)
            return local_next 
        
        def process_chunk(chunk):
            for node in chunk:
                results = process_node(u)
                for sublist in results:
                    for v in sublist:
                        next_level.append(v)
            return next_level
            
        procs = [mp.Process(target=process_chunk, args=(chunk)) for chunk in chunks]
        
        for process in procs:
            while current_level:
                next_level = []
                chunk_size = len(current_level)


        return bfs_tree



if __name__ == "__main__":

    Grafen = Graph.CreateGraph(20, 3)
    s = Graph.mult_init(Grafen, 0, 2)
    
    p = Graph.BFS_Threading(Grafen, 0, 5)
    print(p)


    nx.draw(p, with_labels=True)
    plt.show()
