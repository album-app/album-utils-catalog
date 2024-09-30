###album catalog: album-utils-catalog

from album.runner.api import setup, get_args

env_file = """
channels:
  - conda-forge
dependencies:
  - python=3.10
  - pip
  - "numpy<2"
  - scipy
  - scikit-image
  - joblib
  - scikit-learn==1.3.2
  - pip:
    - album
"""

def run():
    import subprocess

    # Fetch arguments
    args = get_args()
    album_solution_name = args.album_solution_name
    slurm_partition = args.slurm_partition
    slurm_time = args.slurm_time
    slurm_memory = args.slurm_memory
    slurm_cpus_per_task = args.slurm_cpus_per_task
    slurm_gpus = args.slurm_gpus
    slurm_module_commands = args.slurm_module_commands
    extra_args = args.extra_args
    submit_job = args.submit_job

    # Construct the Slurm job script
    slurm_script = f"""#!/bin/bash
#SBATCH --job-name=album_single_job
#SBATCH --output=album_single_job_%j.out
#SBATCH --error=album_single_job_%j.err
#SBATCH --time={slurm_time}
#SBATCH --mem={slurm_memory}
#SBATCH --cpus-per-task={slurm_cpus_per_task}
#SBATCH --gpus={slurm_gpus}
"""

    if slurm_partition:
        slurm_script += f"#SBATCH --partition={slurm_partition}\n"

    if slurm_module_commands:
        slurm_script += f"\n# Load modules\n{slurm_module_commands}\n"

    slurm_script += f"""
# Activate micromamba environment
eval "$(micromamba shell hook --shell=bash)"

export MAMBA_CACHE_DIR=$MYDATA/micromamba_cache/dir_$SLURM_JOB_ID

micromamba_cmd="micromamba run -n album album run {album_solution_name} {extra_args}"
echo "Executing: $micromamba_cmd"
eval $micromamba_cmd
"""

    slurm_script_file = "submit_album_single_job.sh"
    with open(slurm_script_file, 'w') as f:
        f.write(slurm_script)

    # Print or submit the job to Slurm
    if submit_job:
        subprocess.run(["sbatch", slurm_script_file], check=True)
        print(f"Submitted single job for solution '{album_solution_name}' to Slurm.")
    else:
        print(f"Slurm submission command: sbatch {slurm_script_file}")
        with open(slurm_script_file, 'r') as f:
            print(f.read())

setup(
    group="album",
    name="slurm-run",
    version="0.0.1",
    title="Run a solution on slurm the same way you run a solution",
    description="Submit a single album solution to Slurm as a job with customizable resources.",
    solution_creators=["Kyle Harrington"],
    tags=["slurm", "album", "job"],
    license="MIT",
    album_api_version="0.5.1",
    args=[
        {"name": "album_solution_name", "type": "string", "required": True, "description": "Name of the album solution to run."},
        {"name": "slurm_partition", "type": "string", "required": False, "description": "Slurm partition to use."},
        {"name": "slurm_time", "type": "string", "required": False, "default": "24:00:00", "description": "Time limit for the Slurm job (e.g., 01:00:00 for 1 hour)."},
        {"name": "slurm_memory", "type": "string", "required": False, "default": "128G", "description": "Memory limit for the Slurm job (e.g., 128G for 128 GB)."},
        {"name": "slurm_cpus_per_task", "type": "integer", "required": False, "default": 24, "description": "Number of CPUs per Slurm task."},
        {"name": "slurm_gpus", "type": "integer", "required": False, "default": 0, "description": "Number of GPUs per Slurm task."},
        {"name": "slurm_module_commands", "type": "string", "required": False, "description": "Slurm module commands to load necessary modules (e.g., module load cuda/11.8.0\\nmodule load cudnn/8.8.1.3_cuda11)."},
        {"name": "extra_args", "type": "string", "required": False, "default": "", "description": "Additional arguments to pass to the album solution."},
        {"name": "submit_job", "type": "boolean", "required": False, "default": True, "description": "Whether to submit the job to Slurm or just print the submission command and script."}
    ],
    run=run,
    dependencies={
        "environment_file": env_file
    },
)
