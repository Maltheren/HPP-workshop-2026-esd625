from mpi4py import MPI
import numpy as np
from collections import defaultdict, deque
import networkx as nx
import matplotlib.pyplot as plt
import csv
from tqdm import tqdm
import cProfile

# RUNS THIS IN THE TERMINAL, DESCRIBING HOW MANY PROCCESSORS TO START:
# mpiexec –n 10 python MPI_BFS.py
# mpiexec –n 4 python MPI_BFS\MPI_BFS.py


comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()

class Graph:
    def __init__(self):
        self.graph = defaultdict(list)
        # 2D topologi info
        self.cart_comm = None
        self.row_comm = None
        self.col_comm = None
        self.coords = [0, 0]

    def addEdge(self, u, v):
        self.graph[u].append(v)

    def setup_2d_topology(self, num_nodes): 
        # Beregn 2D dimensioner (8 processer 4x2 gitter)
        dims = MPI.Compute_dims(size, 2)
        self.cart_comm = comm.Create_cart(dims, periods=[False, False], reorder=True)
        self.coords = self.cart_comm.Get_coords(rank)
        
        # Sub-communicators til række- og kolonne-kommunikation
        self.row_comm = self.cart_comm.Sub([False, True])  # Samme række
        self.col_comm = self.cart_comm.Sub([True, False])  # Samme kolonne
        return dims

    def partition_2d(self, full_graph_dict, num_nodes):
        dims = self.setup_2d_topology(num_nodes)
        
        def get_range(coord, total, n_procs):
            s = coord * (total // n_procs)
            e = (coord + 1) * (total // n_procs) if coord < n_procs - 1 else total
            return s, e

        # Find ud af hvad denne specifikke rank skal eje
        row_s, row_e = get_range(self.coords[0], num_nodes, dims[0])
        col_s, col_e = get_range(self.coords[1], num_nodes, dims[1])

        if rank == 0:
            # Rank 0 sender bidderne ud
            for r in range(dims[0]):
                for c in range(dims[1]):
                    r_s, r_e = get_range(r, num_nodes, dims[0])
                    c_s, c_e = get_range(c, num_nodes, dims[1])
                    
                    # Filtrer data til 2D-blok (r, c)
                    block = defaultdict(list)
                    for u in range(r_s, r_e):
                        if u in full_graph_dict:
                            # Kun naboer v der lander i denne kolonne-partition
                            neighbors = [v for v in full_graph_dict[u] if c_s <= v < c_e]
                            if neighbors:
                                block[u] = neighbors
                    
                    target_rank = self.cart_comm.Get_cart_rank([r, c])
                    if target_rank == 0:
                        self.graph = block
                    else:
                        comm.send(dict(block), dest=target_rank)
        else:
            self.graph = defaultdict(list, comm.recv(source=0))

        return row_s, row_e, col_s, col_e

    """ 
    def parallel_bfs(self, start_node, num_nodes):
        visited = np.zeros(num_nodes, dtype=bool)
        # Frontier: hvem skal vi tjekke i dette lag?
        frontier = np.zeros(num_nodes, dtype=bool)
        
        if start_node < num_nodes: # En simpel start-betingelse
            frontier[start_node] = True
        
        level = 0
        while frontier.any():
            # 1. Kommuniker frontier internt i rækkerne
            # Alle i rækken skal vide, hvilke noder de skal tjekke
            local_frontier = np.zeros(num_nodes, dtype=bool)
            self.row_comm.Allreduce(frontier, local_frontier, op=MPI.LOR)

            # 2. Find lokale naboer
            discovered_neighbors = np.zeros(num_nodes, dtype=bool)
            for u in range(num_nodes):
                if local_frontier[u] and u in self.graph:
                    for v in self.graph[u]:
                        if not visited[v]:
                            discovered_neighbors[v] = True

            # 3. Kolonne-kommunikation (Allreduce i kolonnen)
            # Vi samler alle naboer fundet i denne kolonne-gruppe
            next_frontier = np.zeros(num_nodes, dtype=bool)
            self.col_comm.Allreduce(discovered_neighbors, next_frontier, op=MPI.LOR)

            # Opdater visited og gør klar til næste lag
            visited |= frontier
            frontier = next_frontier & ~visited
            
            if rank == 0:
                print(f"Level {level} færdig...")
            level += 1

        return visited
    """    
   
    def parallel_bfs(self, start_node, num_nodes):
        distances = np.full(num_nodes, -1, dtype=int)
        
        if start_node < num_nodes:
            distances[start_node] = 0
            
        current_frontier = np.zeros(num_nodes, dtype=bool)
        current_frontier[start_node] = True
        
        level = 1
        while True:
            # Synkroniser stop-betingelse (vigtigt for at undgå deadlock!)
            local_any = current_frontier.any()
            global_any = comm.allreduce(local_any, op=MPI.LOR)
            
            if not global_any:
                break
            
            # 1. Row Allreduce: Del den nuværende frontier horisontalt
            global_frontier = np.zeros(num_nodes, dtype=bool)
            self.row_comm.Allreduce(current_frontier, global_frontier, op=MPI.LOR)

            # 2. Local discovery: Find naboer lokalt
            local_discovered = np.zeros(num_nodes, dtype=bool)
            for u in range(num_nodes):
                if global_frontier[u] and u in self.graph:
                    for v in self.graph[u]:
                        if distances[v] == -1:
                            local_discovered[v] = True

            # 3. Column Allreduce: Saml alle fundne naboer vertikalt
            next_frontier_global = np.zeros(num_nodes, dtype=bool)
            self.col_comm.Allreduce(local_discovered, next_frontier_global, op=MPI.LOR)

            # 4. Opdater frontier og distancer
            current_frontier[:] = False
            for v in range(num_nodes):
                if next_frontier_global[v] and distances[v] == -1:
                    distances[v] = level
                    current_frontier[v] = True
            
            level += 1
            
        return distances


# --- Hjælpefunktioner ---
def nx_to_dict(nx_graph):
    d = defaultdict(list)
    for u, v in nx_graph.edges():
        d[u].append(v)
    return d

def CreateGraph_nx_graph(Nodes, edges, seed, directed=False):
    return nx.gnm_random_graph(Nodes, edges, seed, directed=directed)

def visualize_nx_graph(Graph, title, gravity=False):
    plt.figure(figsize=(8, 6))
    
    if gravity:
        pos = nx.bfs_layout(Graph, 0)
    else:
        pos = nx.spring_layout(Graph)

    nx.draw(Graph, pos, with_labels=True, node_color='lightblue', node_size=500, edge_color='gray')
    plt.title(title)
    plt.show(block=False)

def visualize_matrix_partition(full_dict, num_nodes, dims):
    if rank == 0:
        plt.figure(figsize=(8, 8))
        
        # Lav et grid der viser processernes grænser
        for i in range(dims[0] + 1):
            plt.axhline(i * (num_nodes // dims[0]), color='black', lw=2)
        for j in range(dims[1] + 1):
            plt.axvline(j * (num_nodes // dims[1]), color='black', lw=2)

        # Farv kanterne baseret på hvem der ejer dem
        colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown']
        
        for u, neighbors in full_dict.items():
            for v in neighbors:
                # Find ud af hvilken rank der ejer (u, v) i et 2D layout
                r = min(u // (num_nodes // dims[0]), dims[0] - 1)
                c = min(v // (num_nodes // dims[1]), dims[1] - 1)
                target_rank = r * dims[1] + c # Simpel rank beregning
                
                plt.scatter(v, u, c=colors[target_rank % len(colors)], s=50)

        plt.gca().invert_yaxis() # Så node 0 er øverst til venstre
        plt.title(f"2D Partitionering: Hver farve er en MPI Rank\n(Rækker = Fra Node, Kolonner = Til Node)")
        plt.xlabel("Nabo Node (v)")
        plt.ylabel("Kilde Node (u)")
        plt.grid(True, which='both', linestyle='--', alpha=0.5)

def show_result():
    print("\n" + "="*40)
    print("1. GLOBAL ADJACENCY MATRIX")
    print("="*40)
    
    # Lav overskrift med kolonne-tal
    header = "      " + "".join([f"{i:3}" for i in range(num_nodes)])
    print(header)
    print("    " + "-" * (num_nodes * 3 + 2))

    # Print matricen række for række
    for u in range(num_nodes):
        row_str = f"{u:3} | "
        for v in range(num_nodes):
            # Tjek om der er en kant fra u til v i vores full_dict
            if u in full_dict and v in full_dict[u]:
                row_str += " 1 " # Der er en kant
            else:
                row_str += " . " # Der er ingen kant (punktum er lettere at læse end 0)
        print(row_str)

    print("\n" + "="*40)
    print(f"2. BFS DISTANCER (Start node: {start_node})")
    print("="*40)
    
    # Print distancerne i en overskuelig række
    print("Node:    " + "".join([f"{i:3}" for i in range(num_nodes)]))
    print("Dist:    " + "".join([f"{d:3}" if d != -1 else "  X" for d in global_dists]))
    print("="*40)

if __name__ == "__main__":

    
    test_sizes = [100000]
    iterations = 1 # To ensure normal distribution
    results = []

    if rank == 0:
        print(f"Starter benchmark med {size} processer...")

    for nodes in test_sizes:
        if rank == 0:
            pbar = tqdm(total=iterations, desc=f"Noder: {nodes:<5}", unit="it")
        
        nodes_mean_accumulator = []
        nodes_max_accumulator = []

        for i in range(iterations):
            # 1. NY graf for HVER iteration med unikt seed
            if rank == 0:
                # Vi bruger 'i' som seed, så vi får 100 forskellige grafer
                nx_graf = CreateGraph_nx_graph(nodes, nodes*6, i, True)
                full_dict = nx_to_dict(nx_graf)
            else:
                full_dict = None

            # 2. Setup og kørsel
            local_graph = Graph()
            comm.Barrier()

            pr = cProfile.Profile()
            pr.enable()
            t_start = MPI.Wtime()
            
            local_graph.partition_2d(full_dict, nodes)
            local_graph.parallel_bfs(0, nodes)
            
            t_slut = MPI.Wtime()
            lokal_tid = t_slut - t_start

            # 3. Opsamling (Husk Reduce skal kaldes af alle)
            total_tid_sum = np.zeros(1, dtype=float)
            max_tid_val = np.zeros(1, dtype=float)
            
            comm.Reduce(np.array([lokal_tid]), total_tid_sum, op=MPI.SUM, root=0)
            comm.Reduce(np.array([lokal_tid]), max_tid_val, op=MPI.MAX, root=0)

            pr.disable()
            pr.dump_stats(f'profile_rank_{rank}.prof')

            if rank == 0:
                nodes_mean_accumulator.append(total_tid_sum[0] / size)
                nodes_max_accumulator.append(max_tid_val[0])
                pbar.update(1)

        if rank == 0:
            pbar.close()
            final_mean = sum(nodes_mean_accumulator) / iterations
            final_max = sum(nodes_max_accumulator) / iterations
            results.append([nodes, final_mean, final_max])

    # 4. Gem til CSV (Append mode, så du kan køre -n 1, 4, 8, 12 efter hinanden)
    if rank == 0:
        import os
        csv_filename = "Mikkel_BFS_MPI.csv"
        file_exists = os.path.isfile(csv_filename)
        
        with open(csv_filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            # Skriv kun header hvis filen er ny
            if not file_exists:
                writer.writerow(['procs', 'num_nodes', 'avg_mean_time', 'avg_max_time'])
            
            for row in results:
                writer.writerow([size] + row)
        
        print(f"\nFærdig! Resultater for {size} processer tilføjet til {csv_filename}")