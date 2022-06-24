#!/bin/bash
#SBATCH --nodes=2
#SBATCH --ntasks=8
#SBATCH --ntasks-per-node=4
#SBATCH --cpus-per-task=1
#SBATCH --time=00:05:00
#SBATCH --output=2node8core.out
module load foss/2019b
module load python/3.7.4
module load numpy/1.17.3-python-3.7.4
module load mpi4py/3.0.2-timed-pingpong
srun -n 8 python3 main.py

##DO NOT ADD/EDIT BEYOND THIS LINE##
##Job monitor command to list the resource usage
my-job-stats -a -n -s