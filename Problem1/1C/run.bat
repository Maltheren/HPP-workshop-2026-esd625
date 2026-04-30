@echo off

for /L %%n in (2,2,16) do (
    echo Running with n=%%n
    mpiexec -n %%n python ./MPI_BFS.py
    echo -----------------------------
)

pause