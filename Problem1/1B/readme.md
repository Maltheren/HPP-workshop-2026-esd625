# Shared Memory BFS
Hello,

This folder contains a shared memory version of BFS which runs on randomly generated graphs.

The SharedMemoryBFS.py program contains a sequential version for speed comparison, although it should be noted that they do not output the same result, although both solutions are correct. Thus, you cannot check for correctness by comparing the output graphs directly. 

In the bottom of the program the creation of the graph can be modified to fit your needs, but the BFS's run on Graph objects, as defined in the top of the document. 

## Running the code
Adjust the size of the graph, the maximum allowed number of edges per node (The number of edges is distributed randomly up to a point), and number of processes for multiprocessing. 

Note that the parallel code is much (MUCH) slower than the sequential code. So it's not broken just because nothing's happening ._.
