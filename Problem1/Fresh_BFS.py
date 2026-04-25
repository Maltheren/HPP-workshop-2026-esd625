import multiprocessing as mp
from collections import defaultdict, deque
import random as rand
import numpy as np
import tqdm as tqdm
import networkx as nx
import matplotlib.pyplot as plt
import time

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
    
    def BFS(graph: nx.Graph, start: int, layer: int):
        bfs_tree = nx.Graph()
        queue = deque([start])
        graph.nodes[start]['visited'] = True
        print(graph.nodes[start])
        
        while queue:
            u = queue.popleft()
            for v in graph.adj[u]:
                if graph.nodes[v]['visited'] == False:
                    graph.nodes[v]['visited'] = True
                    graph.nodes[v]['Layer'] = layer
                    queue.append(v)
                    bfs_tree.add_edge(u, v)

            layer += 1
                    


       
        return bfs_tree


if __name__ == "__main__":

    Grafen = Graph.CreateGraph(20, 3)
    s = Graph.mult_init(Grafen, 0, 2)
    
    p = Graph.BFS(Grafen, 0, 0)
    print(p)


    nx.draw(p, with_labels=True)
    plt.show()




















    """SHAME CORNER:

            while len(start_points) < threads:
            if threads < len(neighbours)+len(start_points):
                for i in range(threads-len(start_points)):
                    start_points.append(neighbours[i])
            else:
                for i in range(len(neighbours)):
                    start_points.append(neighbours[i])

                n = start_points[0]
                print("s",len(start_points))
                neighbours = list(graph.adj[n])
            tries += 1
            if tries > threads*2:
                break
                
                
    """