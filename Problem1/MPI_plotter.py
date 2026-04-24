import pandas as pd
import matplotlib.pyplot as plt
import io



df = pd.read_csv('Problem1/bfs_master_benchmark_2.csv')

# Initialize the plot
plt.figure(figsize=(10, 6))

# Plot each processor count as a separate line
for proc in sorted(df['procs'].unique(), reverse=True):
    subset = df[df['procs'] == proc]
    plt.plot(subset['num_nodes'], subset['avg_mean_time'], marker='o', label=f'Procs: {proc}')

# Formatting the plot
plt.xlabel('Number of Nodes (log scale)')
plt.ylabel('Average Mean Time (log scale)')
plt.title('Performance Scaling: Mean Time vs. Number of Nodes')
plt.legend()
plt.grid(True, which="both", ls="-", alpha=0.5)

# Use log-log scale for better visibility of scaling trends
plt.xscale('log')
plt.yscale('log')

plt.show()