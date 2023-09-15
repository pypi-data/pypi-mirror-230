#!/bin/bash
#
#SBATCH -J climix-test
#SBATCH -t 06:00:00
#SBATCH -N 16
#SBATCH --exclusive
#SBATCH --ntasks-per-node=4
#

module load Mambaforge
conda activate climix-devel

COORDINATE_DIR=/nobackup/...

cd $COORDINATE_DIR

mpirun climix -i -e -d mpi \
         -x tn90pctl \
         /home/rossby/imports/cordex/EUR-11/CLMcom-CCLM4-8-17/v1/ICHEC-EC-EARTH/r12i1p1/rcp85/bc/links-hist-scn/day/tasmin_EUR-11_ICHEC-EC-EARTH_rcp85_r12i1p1_CLMcom-CCLM4-8-17_v1_day_*.nc

# Script ends here
