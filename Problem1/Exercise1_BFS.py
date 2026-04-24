from collections import defaultdict, deque
import random as rand
import numpy as np
import tqdm as tqdm
import networkx as nx
import matplotlib.pyplot as plt
import time

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


def run_test(Graf: Graph):
    t_0 = time.perf_counter_ns()
    BFS_TREE = Graf.BFS(0)
    t_1 = time.perf_counter_ns()
    #visualizeGraph(BFS_TREE,"Jeg er et træ", True)

    return t_1 - t_0



def sequintelTest():
    Nodes = [10000, 100000]
    Edges_prNode = [5, 5]
    runs = 100



    for (num_nodes, num_edges) in zip(Nodes, Edges_prNode):
        t_perf = np.zeros(runs)

        for i in tqdm.tqdm(range(runs)):
            Graf = CreateGraph(num_nodes, num_edges)
            #visualizeGraph(Graf,"Kludder kage", False)

            t_perf[i] = run_test(Graf) /1000 # Omregn til mikrosekunder
            
        print(f"Det tog {t_perf.mean():0.1f} us, std: {t_perf.std():0.1f} us")


        

if __name__ == "__main__":
       
    graf1 = CreateGraph(15, 20)

    tree = nx.bfs_tree(graf1, 0)
    

    plt.show()
    #sequintelTest()        # Lavet til det sequintielle .
    