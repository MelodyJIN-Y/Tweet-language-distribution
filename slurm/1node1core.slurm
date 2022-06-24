#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --time=00:10:00
#SBATCH --output=1node1core.out
module load foss/2019b
module load python/3.7.4
module load numpy/1.17.3-python-3.7.4
module load mpi4py/3.0.2-timed-pingpong
srun -n 1 python3 main.py

##DO NOT ADD/EDIT BEYOND THIS LINE##
##Job monitor command to list the resource usage
my-job-stats -a -n -s