#!/bin/bash
#
#SBATCH -J climix
#SBATCH -t 10:00:00
#SBATCH -N 1 --exclusive
#SBATCH hetjob
#SBATCH -N 16 --exclusive --cpus-per-task=2
#SBATCH hetjob
#SBATCH -N 1 --exclusive

# General approach
# ----------------
# We use slurm's heterogeneous job support for climix, using three components.
# The first component contains the dask scheduler, the second component runs
# the workers, and the third the client, i.e. climix itself. Neither scheduler
# nor client are naturally parallel, and could share a single node. However,
# giving each their own aleviates otherwise possible memory pressure. The
# workers bring the scaling parallelism and can be run on an arbitrary number of
# nodes, depending on the size of the data and time and memory contraints. Note
# that we often want to use several nodes purely to gain access to sufficient
# memory.
#
# Bi specific notes
# -----------------
# Cores
# ~~~~~
# As of this writing, bi nodes are setup with hyperthreading active, with every
# node having 32 virtual cores provided by 16 physical cores. We want the
# workers to use 16 threads total per node, thus using all physical cores but
# avoiding conflicts due to hyperthreading. We achieve this by running 8 worker
# processes with 2 threads each on every node. This is implemented via slurm's
# `--cpus-per-task=2` option, which instructs slurm to start one task for every
# cpu. That means that the number of nodes can be freely chosen using the `-N`
# option in the header at the top of this file.
#
# Memory
# ~~~~~~
# Every normal (`thin`) node has 64GB of memory and there is a small number of
# `fat` nodes with 256GB of memory.
# The workers are run on normal nodes. To allow for a little bit of breathing
# room for the system and other programs, we use 90% of the available memory,
# equally distributed among the worker processes (or equivalently slurm tasks)
# on each node for a total of 7.2GB per worker.
# Scheduler and client run on their own nodes. If memory becomes a limiting
# factor for either of those, these nodes can be chosen as `fat` nodes by adding
# the `-C fat` switch to the corresponding SBATCH line at the top of this file.

NO_SCHEDULERS=1
NO_PROGRAM=1

TOTAL_WORKER_CPUS=$(echo $SLURM_JOB_CPUS_PER_NODE_HET_GROUP_1 |sed 's/(x\([0-9]*\))/*\1/g;s/,/+/g'|bc)
echo "$TOTAL_WORKER_CPUS from $SLURM_JOB_CPUS_PER_NODE_HET_GROUP_1"
NO_WORKERS=$(($TOTAL_WORKER_CPUS / $SLURM_CPUS_PER_TASK_HET_GROUP_1))
MEM_PER_WORKER=$(echo "$SLURM_CPUS_PER_TASK_HET_GROUP_1 * $SLURM_CPUS_PER_TASK_HET_GROUP_1 * $SLURM_MEM_PER_CPU_HET_GROUP_1 * .9" | bc -l)

echo "Total number of workers: $NO_WORKERS"
echo "Memory per worker in MB: $MEM_PER_WORKER"

module load Mambaforge
conda activate climix-devel

COORDINATE_DIR=/nobackup/...

cd $COORDINATE_DIR

SCHEDULER_FILE=$COORDINATE_DIR/scheduler-$SLURM_JOB_ID.json

# Start scheduler

SCHEDULER_COMMAND="--het-group=0 --ntasks $NO_SCHEDULERS --kill-on-bad-exit=1 \
                   dask scheduler \
                   --interface ib0 \
                   --scheduler-file $SCHEDULER_FILE"

WORKERS_COMMAND="--het-group=1 --ntasks $NO_WORKERS --kill-on-bad-exit=1 \
                 dask worker \
                 --interface ib0 \
                 --scheduler-file $SCHEDULER_FILE \
                 --memory-limit ${MEM_PER_WORKER}MB \
                 --death-timeout 120 \
                 --nthreads 2"

srun $SCHEDULER_COMMAND : \
     $WORKERS_COMMAND : \
     --het-group=2 --ntasks $NO_PROGRAM --kill-on-bad-exit=1 \
     climix -e -s -d external@scheduler_file=$SCHEDULER_FILE \
       -x tn90pctl \
       /home/rossby/imports/cordex/EUR-11/CLMcom-CCLM4-8-17/v1/ICHEC-EC-EARTH/r12i1p1/rcp85/bc/links-hist-scn/day/tasmin_EUR-11_ICHEC-EC-EARTH_rcp85_r12i1p1_CLMcom-CCLM4-8-17_v1_day_*.nc

# wait


# Script ends here
