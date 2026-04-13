#!/bin/bash
#SBATCH --job-name=wwtp_scenario_sweep
#SBATCH --nodes=1
#SBATCH --gpus-per-node=1
#SBATCH --time=02:00:00
#SBATCH --array=0-999
#SBATCH --output=logs/scenario_%A_%a.out

# Load container
srun --container-image=nvcr.io/nvidia/pytorch:24.01-py3 \
     --container-mounts=$(pwd):/workspace \
     python /workspace/stage1_5_wwtp_dc/run_demo.py \
       --scenario-id ${SLURM_ARRAY_TASK_ID} \
       --weather-variation 0.${SLURM_ARRAY_TASK_ID} \
       --output /workspace/data/sweep/scenario_${SLURM_ARRAY_TASK_ID}.csv

# This script demonstrates:
# - Parallel BSM1 scenario generation across GPU nodes
# - Container-based reproducibility
# - Array jobs for parameter sweeps
# Production use: finding optimal BESS dispatch parameters via sweep
