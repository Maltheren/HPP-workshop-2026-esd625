from collections import defaultdict, deque
import numpy as np
import tqdm as tqdm
import networkx as nx
import matplotlib.pyplot as plt
import time
from multiprocessing import Process, Manager
import math




class Graph:
    def __init__(self):
        self.graph = defaultdict(list)

    def addEdge(self, u, v):
        self.graph[u].append(v)


def BFS(graph: Graph, start: int):
    visited = set()
    bfs_tree = Graph()
    queue = deque([start])
    visited.add(start)

    while queue:
        u = queue.popleft()
        #print (s, end = " ")
        for v in graph.graph[u]:
            if v not in visited:
                visited.add(v)
                queue.append(v)
                bfs_tree.addEdge(u, v)
        
    return bfs_tree

def process_block(block, visited, graph_global, bfs_tree_global, next_level): #Jeg tjekker en blok noder og finder deres næste lag
    local_next = set()

    for node in block:
        temp_vector = [node]
        for v in graph_global[node]:
            if v not in visited:
                visited.add(v)
                local_next.add(v)
                temp_vector.append(v)
                #print(f"Adding edge from {node} to {v}")
        bfs_tree_global[node] = temp_vector
    
    #Returner de fundne vertices i næste level
    for item in local_next:
        next_level.add(item)
    return 




def BFS_threaded(start: int, threads: int, graph: Graph):
    
    with Manager() as manager: # Starter en manager for at håndtere delte data strukturer
        globalGraph = manager.list()
        globalGraph = graph.graph
        visited = manager.set()
        bfs_tree = manager.list([None]*num_nodes)

        
        # Vi starter data structs op
        visited.add(start)
        current_level = []

        # Vi finder det første lag
        first_level = set()
        temp_vector = [start]
        for v in Graf.graph[start]:
                visited.add(v)
                first_level.add(v)
                temp_vector.append(v)
        
        bfs_tree[0] = temp_vector

        current_level = list(first_level)


        blocks = []
        
        if len(current_level) < threads:
            num_of_processes = len(current_level)
        else: num_of_processes = threads
        
        while current_level: 
            next_level = manager.set() #Empties the next level
            blocks = []
            block_length = int(math.ceil(len(current_level)/num_of_processes)) #Partitions the level into blocks
            for i in range(0, num_of_processes):
                blocks.append(current_level[i*block_length:(i+1)*block_length])
        
            #We use processes because pooling didn't work with the data types we like.
            processes = [Process(target=process_block, args=(blocks[i],visited, globalGraph, bfs_tree, next_level, )) for i in range(num_of_processes)]
            for p in processes:
                p.start()
            for p in processes:
                p.join()
            current_level = list(next_level)
        
        bfs_graph = Graph()
        for node in list(bfs_tree):
            if node is not None:
                for i in range(len(node[1:])):
                    bfs_graph.addEdge(node[0], node[i+1])
        return bfs_graph
    

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


def CreateGraph(num_nodes: int, max_edges_pr_node: int):
    graph = Graph()
    Node_candidates = np.arange(num_nodes)
    for node in Node_candidates:
        for _ in range(np.random.randint(0, max_edges_pr_node)):
            dest_node = node
            while(dest_node == node):
                dest_node = np.random.randint(0, len(Node_candidates)-1) # Rolls the dice prays its not the same node
            graph.addEdge(node, dest_node)
    return graph



def run_test_unthreaded(graph: Graph):
    t_0 = time.perf_counter_ns()
    BFS_TREE = BFS(graph, 0)
    t_1 = time.perf_counter_ns()
    #visualizeGraph(BFS_TREE,"Jeg er et træ", True)
    #plt.show()

    return t_1 - t_0


def run_test_threaded(graph: Graph, processors: int):
    t_0 = time.perf_counter_ns()
    BFS_TREE = BFS_threaded(0, processors, graph)
    t_1 = time.perf_counter_ns()
    #visualizeGraph(BFS_TREE,"Jeg er et træ", True)
    #plt.show()

    return t_1 - t_0


if __name__ == "__main__":
    #_____________________________________________________________________________________________
    #=========================[VARY CODE FOR TEST PURPOSES HERE:]=================================
    #_____________________________________________________________________________________________
    num_nodes = 4000
    num_edges = 4
    processors = 10  

    #_____________________________________________________________________________________________
    #=============================================================================================
    #_____________________________________________________________________________________________
   
    
    Graf = CreateGraph(num_nodes, num_edges)            #Creates the shared graf for testing
    print("Graf is done")
    
    time1 = run_test_unthreaded(Graf) / 1e9             #Run the standard BFS Algo
    print(f"time single: {time1}")

    time2 = run_test_threaded(Graf, processors) / 1e9   #Run the level synchronized shared memory parallel BFS
    print(f"time threaded: {time2}")

    print(f"Speedup: {time1 / time2:.8f}x")             #Find speedup for parrallel BFS compared to normal BFS
                                                            #(More like slowdown)
