from multiprocessing import Pool
from collections import defaultdict, deque


import random as rand
import numpy as np
import tqdm as tqdm
import networkx as nx
import matplotlib.pyplot as plt
import time

import asyncio
from concurrent.futures import ThreadPoolExecutor


def process_node_worker(u, graph_data, visited_shared): 
    local_next = []
    # Note: Shared state logic needs to be handled carefully in parallel
    for v in graph_data.get(u, []):
        if v not in visited_shared:
            visited_shared.add(v)
            local_next.append(v)
            bfs_tree.addEdge(u, v)    
    return local_next

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

        return bfs_tree
    

    def BFS_Threading(self, start, threads):
        bfs_tree = Graph()
        visited = set()
        visited.add(start)
        current_level = [start]
        
        """def process_node(u): 
        local_next = []
        for v in self.graph[u]:
            if v not in visited:
                visited.add(v)
                bfs_tree.addEdge(u, v)
                local_next.append(v)
        return local_next """
            

        with Pool(5) as pool:
            while current_level:
                next_level = []
                chunks = int(len(current_level)/threads)
                args = [(u, self.graph, visited) for u in current_level]
                results = pool.starmap(process_node_worker, args)
                for sublist in results:
                    for v in sublist:
                        next_level.append(v)
                
                current_level = next_level


        return bfs_tree



def visualizeGraph(graph_obj, title: str, gravity=False):
    G = nx.DiGraph()

    # Vi løber igennem din defaultdict og tilføjer kanterne til NetworkX
    for u in graph_obj.graph:
        for v in graph_obj.graph[u]:
            G.add_edge(u, v)
    
    plt.figure(figsize=(8, 6))
    
    if gravity:
        pos = nx.bfs_layout(G, 0)    
    else: 
        pos = nx.spring_layout(G)  # Bestemmer hvordan noderne placeres pænt
    
    nx.draw(G, pos, with_labels=True, node_color='lightblue', 
            node_size=15000 / len(graph_obj.graph), edge_color='gray')
    
    plt.title(title)
    plt.show(block=False)


    
def CreateGraph (num_nodes: int, max_edges_pr_node: int):
    graph = Graph()
    ##Vi har nu spawnet så mange tilfædlige noder
    Node_candidates = np.arange(num_nodes)
    outgoing_arrows = np.array([False]*len(Node_candidates) )

    for node in Node_candidates:
        for i in range(np.random.randint(1, max_edges_pr_node)):
            dest_node = node
            tries = 0
            ok = True
            while (dest_node == node or outgoing_arrows[dest_node]):
                dest_node = np.random.randint(0, len(Node_candidates)-1)
                if(tries > max_edges_pr_node*2):
                    ok = False
                    break
                tries += 1
            if(ok):
                #graph.addEdge(node, dest_node)
                graph.addEdge(node, dest_node)
                outgoing_arrows[node] = True

            

    return graph

def run_testSeq(Graf: Graph):
    t_0 = time.perf_counter_ns()
    BFS_TREE = Graf.BFS(0)
    t_1 = time.perf_counter_ns()
    #visualizeGraph(BFS_TREE,"Jeg er et træ", True)

    return t_1 - t_0

def run_testPar(Graf: Graph):
    t_0 = time.perf_counter_ns()
    BFS_TREE = Graf.BFS_Threading(0, 10)
    t_1 = time.perf_counter_ns()
    #visualizeGraph(BFS_TREE,"Jeg er et træ", True)

    return t_1 - t_0



def sequintelTest(nodes):
    Nodes = [nodes, nodes]
    Edges_prNode = [10, 10]

    for (num_nodes, num_edges) in zip(Nodes, Edges_prNode):
        t_perf = np.zeros(runs)

        for i in tqdm.tqdm(range(runs)):
            Graf = CreateGraph(num_nodes, num_edges)
            #visualizeGraph(Graf,"Kludder kage", False)

            t_perf[i] = run_testSeq(Graf) /1000 # Omregn til mikrosekunder
            #print("SRun", i, "took", t_perf[i], "ms")
        print(f"Sequential: Det tog {t_perf.mean():0.1f} us, std: {t_perf.std():0.1f} us")


def SharedParaTest(nodes):
    Nodes = [nodes,nodes]
    Edges_prNode = [10, 10]

    for (num_nodes, num_edges) in zip(Nodes, Edges_prNode):
        t_perf = np.zeros(runs)

        for i in tqdm.tqdm(range(runs)):
            Graf = CreateGraph(num_nodes, num_edges)
            #visualizeGraph(Graf,"Kludder kage", False)

            t_perf[i] = run_testPar(Graf) /1000 # Omregn til mikrosekunder
            #print("PRun", i, "took", t_perf[i], "ms")
            
        print(f"Shared Para:Det tog {t_perf.mean():0.1f} us, std: {t_perf.std():0.1f} us")

def Versus(nodes, edges):
    Graf = CreateGraph(nodes, edges)
    #visualizeGraph(Graf,"Kludder kage", False)

    t_seq = run_testSeq(Graf) /1000 # Omregn til mikrosekunder
    t_par = run_testPar(Graf) /1000 # Omregn til mikrosekunder

    print(f"Sequential: Det tog {t_seq:0.1f} us")
    print(f"Shared Para:Det tog {t_par:0.1f} us")
    
        

if __name__ == "__main__":


    nodes = 4000
    edges = 30
    runs = 10
    #    plt.show()
    #sequintelTest(nodes)        # Lavet til det sekventielle.
    #SharedParaTest(nodes)       # Lavet til det paralelle. 
    #Versus(nodes, edges)

    Grafen = CreateGraph(200, 5)
    #print(Grafen.graph)
    Res1 = Grafen.BFS(0)
    #print(Res1.graph)
    Res2 = Grafen.BFS_Threading(0,10)
    #print(Res2.graph)  

    visualizeGraph(Grafen, "Original Graf", False)
    plt.show()
    visualizeGraph(Res1, "BFS Sequential", True)
    plt.show()
    visualizeGraph(Res2, "BFS Parallel", True)
    plt.show() 
   
    print(f"Are they the same? {Res1 == Res2}")