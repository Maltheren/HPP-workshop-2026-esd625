# Problem 1C
This is an MPI implementation of the BFS.
All the packages are compress into a requirements.txt file, that can be executed into a venv if required.

The whole structure of the implementation is made into a class Graph where it is possible to:
- Create the graph
- Use 1D partitioning scheme
- Do parallel BFS on the 1D partitioned graph
- Use 2D partitioning scheme
- Do parallel BFS on the 2D partitioned graph

There's also a couple helping functions:
- Visualize graph
- Visualize matrix partition
- Create and visualize nx graph (a package used to make graph objects)
- Convert nx graph into dictionary


## Running the code
A list "test_sizes" is the amount of different runs it does, with varying tree sizes.

A iteration variable is the amount of total runs it does. We used it to do 32 runs and then plottet that data since it is over 30 it would be "normal distributed".

Before starting the code, a csv_filename is required to be able to use the MPI_plotter.py.

Also a run.bat file is made which runs this program automatically with the different processors the pc have, starting from 2 and jumping an increment (which is in the run.bat file) (2,2,16) (start processor, increment, Max processor)

The timing is only made for doing the parallel BFS and not including the partitioning scheme.