
"""
Script to submit tasks in a Ploomber pipeline as SLURM jobs.
"""
from pathlib import Path
import subprocess

from jinja2 import Template
from ploomber.spec import DAGSpec

# template that generates the file to execute via sbatch
job_sh = Template("""\
#!/bin/bash
#SBATCH --job-name={{name}}
#SBATCH --output=result.out
#

source ml-basic-env/bin/activate
srun ploomber task {{name}}
""")

# load pipeline.yaml as a DAG object
dag = DAGSpec('pipeline.yaml').to_dag().render()

# maps task name to SLURM job id
name2id = {}

# iterate over tasks
for name, task in dag.items():

    # generate script and save
    script = job_sh.render(name=name)
    Path('_job.sh').write_text(script)

    # does the task have dependencies?
    if task.upstream:
        # if yes, then use --dependency=afterok:
        ids = ':'.join(
            [name2id[task_name] for task_name in task.upstream.keys()])
        # docs: https://hpc.nih.gov/docs/job_dependencies.html
        args = [
            'sbatch', f'--dependency=afterok:{ids}', '--parsable', '_job.sh'
        ]
    else:
        # if no, just submit
        args = ['sbatch', '--parsable', '_job.sh']

    # print the submitted command
    print(' '.join(args))

    # submit job
    res = subprocess.run(args, capture_output=True, check=True)

    # retrieve the job id, we'll use this to register --dependency
    name2id[name] = res.stdout.decode().strip()
