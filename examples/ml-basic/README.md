

# Basic ML project

<!-- start description -->
This pipeline downloads data, cleans it, generates features and trains a model.
<!-- end description -->

## Description

Let's take a look at the `pipeline.yaml`:

<!-- #md -->
```yaml
# Content of pipeline.yaml
# # enable client if you want to upload arfifacts to google cloud storage
# # see clients.py for details
# clients:
#   File:
#     dotted_path: clients.get_storage_client
#     run_id: '{{run_id}}'

tasks:
    # tasks.get, features and join are python functions
  - source: tasks.get
    product: output/get.parquet

  - source: tasks.features
    product: output/features.parquet

  - source: tasks.join
    product: output/join.parquet

    # fit.py is a script executed as a notebook
  - source: fit.py
    name: fit
    product:
        nb: output/nb.ipynb
        model: output/model.pickle

```
<!-- #endmd -->

Note that the first three tasks as Python functions, while the last one is a
script.

Start conda
 
    eval "$($HOME/miniconda/bin/conda shell.bash hook)"

Install ploomber in the base environment so we can download an example and submit the jobs

    pip install ploomber

Download sample pipeline to ml-basic/

    ploomber examples -n templates/ml-basic -o ml-basic
    cd example

Create the project's virtual env
 
    python -m venv myproj
    source myproj/bin/activate
    pip install -r requirements.txt

Copy submit.py (see source code below) to example/submit.py, then submit to the cluster with:
  
    python submit.py
   
If all works, you'll see an example/output folder with:

    features.parquet
    get.parquet
    join.parquet
    Model.pickle
    nb.ipynb

Submit.py:

    """
    Script to submit tasks in a Ploomber pipeline as SLURM jobs.
    """
    from pathlib import Path
    import subprocess

    from jinja2 import Template
    from ploomber.spec import DAGSpec

    from ploomber.constants import TaskStatus

    # template that generates the file to execute via sbatch
    job_sh = Template("""\
    #!/bin/bash
    #SBATCH --job-name={{name}}
    #SBATCH --output=/dev/null
    #SBATCH --partition=short
    #SBATCH -c 1 
    #SBATCH --mem=1g

    # source myproj/bin/activate -- slurm usually passes through env variables, 
    ploomber task {{name}}
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
    
    if  task.exec_status == TaskStatus.Skipped: 
        print("Skipping up-to date task: ", name)
        continue

    # does the task have dependencies?
    if task.upstream:
        # if yes, then use --dependency=afterok:
        ids = ':'.join(
            [name2id[task_name] for task_name in task.upstream.keys() if task_name in name2id])
    else: 
        ids = []    

    #if a task has up-to date upstream dependencies, them the list of ids might be empty and there are effectively no deps
    if len(ids)>0:
        # docs: https://hpc.nih.gov/docs/job_dependencies.html
        args = ['sbatch', f'--dependency=afterok:{ids}']
    else:
        # if no, just submit
        args = ['sbatch']

    args = args + ['--parsable', '_job.sh']
    # print the submitted command
    print(name,': ',' '.join(args))
    
 
    # submit job
    res = subprocess.run(args, capture_output=True, check=True)

    # retrieve the job id, we'll use this to register --dependency
    name2id[name] = res.stdout.decode().strip()
