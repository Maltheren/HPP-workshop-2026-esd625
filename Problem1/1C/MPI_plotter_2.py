import pandas as pd
import matplotlib.pyplot as plt

# Indlæs data
df = pd.read_csv('MPI_WITH_SPEEDUP_75.csv')

# Initialisér plottet (brug f.eks. plt.subplots)
fig, ax = plt.subplots(figsize=(10, 6))

# Sorter de unikke værdier af num_nodes, så legenden står i en pæn rækkefølge
for nodes in sorted(df['num_nodes'].unique()):
    # Filtrér data for det specifikke antal nodes og sortér efter procs
    subset = df[df['num_nodes'] == nodes].sort_values('procs')
    
    # Plot procs på x-aksen og avg_speedup på y-aksen
    ax.plot(subset['procs'], subset['avg_speedup'], marker='o', label=f'Nodes: {nodes}')

plt.xlabel('Procs')
plt.ylabel('Speedup (log scale)')
plt.title('Performance Scaling: Mean Time vs. Number of Nodes')
plt.legend()
plt.grid(True, which="both", ls="-", alpha=0.5)

# Use log-log scale for better visibility of scaling trends
#plt.xscale('log')
#plt.yscale('log')

plt.show()