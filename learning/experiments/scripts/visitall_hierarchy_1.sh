#!/bin/bash
#
#SBATCH -J visitall_hierarchy_1
#SBATCH -t 7-00:00:00
#SBATCH -C thin --exclusive
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=dominik.drexler@liu.se

bash ./visitall.sh hierarchy 1
