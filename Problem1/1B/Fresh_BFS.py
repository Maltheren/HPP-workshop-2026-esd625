import multiprocessing as mp
from multiprocessing import Manager
from collections import deque
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

class Graph:

    @staticmethod
    def CreateGraph(num_nodes: int, max_edges_pr_node: int):
        graph = nx.Graph()
        for i in range(num_nodes):
            graph.add_node(i, visited=False, Layer=0)
            node_edges = np.random.randint(1, max_edges_pr_node)
            tries = 0
            while node_edges > 0:
                dest_node = np.random.randint(0, num_nodes - 1)
                if dest_node != i:
                    graph.add_edge(i, dest_node)
                    node_edges -= 1
                tries += 1
                if tries > max_edges_pr_node * 2:
                    break
        return graph

    @staticmethod
    def BFS(adj: dict, node_data: dict, start: int, layer: int):
        bfs_tree_edges = []
        queue = deque([start])
        
        # safely mark start node using the shared dict
        entry = node_data[start]
        entry['visited'] = True
        entry['Layer'] = layer
        node_data[start] = entry          # must reassign — Manager dicts don't
                                          # detect in-place mutations

        while queue:
            u = queue.popleft()
            for v in adj[u]:
                entry = node_data[v]
                if not entry['visited']:
                    entry['visited'] = True
                    entry['Layer'] = node_data[u]['Layer'] + 1
                    node_data[v] = entry  # reassign to push change to shared memory
                    queue.append(v)
                    bfs_tree_edges.append((u, v))

        return bfs_tree_edges             # return edges instead of nx.Graph
                                          # since nx.Graph isn't picklable for multiprocessing

    @staticmethod
    def mult_init(adj: dict, start: int, threads: int):
        neighbours = list(adj[start])
        return neighbours[:min(threads, len(neighbours))]

    @staticmethod
    def mult_controller(graph: nx.Graph, start: int, threads: int):
        with Manager() as manager:
            # copy node attributes into shared manager dict
            node_data = manager.dict({
                n: manager.dict({'visited': False, 'Layer': 0})
                for n in graph.nodes
            })
            # copy adjacency into a plain dict (structure is read-only, safe to share)
            adj = {n: list(graph.adj[n]) for n in graph.nodes}

            # mark root
            root_entry = node_data[start]
            root_entry['visited'] = True
            root_entry['Layer'] = 0
            node_data[start] = root_entry

            start_points = Graph.mult_init(adj, start, threads)

            # pre-mark all layer 1 start points before workers begin
            for node in start_points:
                entry = node_data[node]
                entry['visited'] = True
                entry['Layer'] = 1
                node_data[node] = entry

            with mp.Pool(processes=len(start_points)) as pool:
                results = pool.starmap(
                    Graph.BFS,
                    [(adj, node_data, node, 1) for node in start_points]
                )

            # merge subtrees
            full_tree = nx.Graph()
            full_tree.add_node(start)
            for node, edges in zip(start_points, results):
                full_tree.add_edge(start, node)
                full_tree.add_edges_from(edges)

        return full_tree


if __name__ == "__main__":
    Grafen = Graph.CreateGraph(2000, 20)

    p = Graph.mult_controller(Grafen, 0, 10)

    nx.draw(Grafen, with_labels=True)
    plt.show()
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
