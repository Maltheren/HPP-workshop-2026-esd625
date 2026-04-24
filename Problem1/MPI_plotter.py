import pandas as pd
import matplotlib.pyplot as plt
import io
import csv

# Load the data
with open('bfs_master_benchmark.csv', 'r') as f:
    data = f.read()

df = pd.read_csv(io.StringIO(data))

# Initialize the plot
plt.figure(figsize=(10, 6))

# Plot each processor count as a separate line
for proc in sorted(df['procs'].unique(), reverse=True):
    subset = df[df['procs'] == proc]
    plt.plot(subset['num_nodes'], subset['avg_mean_time'], marker='o', label=f'Procs: {proc}')

# Formatting the plot
plt.xlabel('Number of Nodes')
plt.ylabel('Average Mean Time (seconds)')
plt.title('Performance Scaling: Mean Time vs. Number of Nodes')
plt.legend()
plt.grid(True, which="both", ls="-", alpha=0.5)

# Use log-log scale for better visibility of scaling trends

plt.show()