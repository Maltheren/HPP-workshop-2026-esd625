from collections import defaultdict, deque
import random as rand
import numpy as np
import tqdm as tqdm
import networkx as nx
import matplotlib.pyplot as plt
import time
import pandas as pd
import seaborn as sns
from multiprocessing import Pool, cpu_count


class Graph:
    def __init__(self):
        self.graph = defaultdict(list)

    def addEdge(self, u, v):
        self.graph[u].append(v)


def BFS(graph: Graph, start: int):
    bfs_tree = Graph()
    visited = set()
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


def CreateGraph_DAG(num_nodes: int, max_edges_pr_node: int):
    graph = Graph()
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
                graph.addEdge(node, dest_node)
                outgoing_arrows[node] = True
    return graph


def run_test(Graf: Graph):
    t_0 = time.perf_counter_ns()
    BFS_TREE = BFS(Graf, 0)
    t_1 = time.perf_counter_ns()
    #visualizeGraph(BFS_TREE,"Jeg er et træ", True)

    return t_1 - t_0



def _single_run(args):
    num_nodes, num_edges = args
    Graf = CreateGraph(num_nodes, num_edges)
    return run_test(Graf) / 1000  # mikrosekunder


def test_sequential_bfs() -> pd.DataFrame:
    Nodes = np.array([100, 200, 300, 400, 500, 600, 700, 800, 900, 1000])
    Edges_prNode = np.floor(Nodes / 3)
    runs = 100

    time_vector = []
    edges_vector = []
    nodes_vector = []

    with Pool(cpu_count()) as pool:
        for num_nodes, num_edges in zip(Nodes, Edges_prNode):
            print(f"testing: nodes={num_nodes}, edges={num_edges}")

            # Lav input til pool
            tasks = [(num_nodes, num_edges)] * runs

            # tqdm wrapper omkring imap
            results = list(tqdm.tqdm(pool.imap(_single_run, tasks), total=runs))

            t_perf = np.array(results)

            # Logging
            edges_vector.extend([num_edges] * runs)
            nodes_vector.extend([num_nodes] * runs)
            time_vector.extend(t_perf)

            print(f"mean={t_perf.mean():0.1f} us, std={t_perf.std():0.1f} us")

    return pd.DataFrame({
        "time": time_vector,
        "nodes": nodes_vector,
        "edges": edges_vector,
    })
        

if __name__ == "__main__":
    
    ##result = test_sequential_bfs()
    ##result.to_csv("results.csv")
    result = pd.read_csv("results.csv")
    result = result[result["time"] < 400]
    #sns.histplot(data=result, x="time", hue="nodes")
    sns.lineplot(data=result, x="nodes", y="time", errorbar=("sd", 2))
    sns.scatterplot(data=result, x="nodes", y="time", size=1)
    plt.grid(True)
    plt.xlabel("Number of nodes")
    plt.ylabel("BFS time, us")
    plt.ylim(0, 200)
    plt.show()