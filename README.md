# Ploomber-on-SLURM
A repository with insturctions on how to boot Ploomber examples using SLURM with the examples and their explanations.

Requirements:

To use RCI cluster you'll have to:
  - 1)Request access for it , use this page:
https://login.rci.cvut.cz/wiki/doku.php
  - 2)Install an SSH client to be able connect to RCI cluster:
 The SSH client is required to connect RCI cluster. For interactive work with GUI applications, X11 server is required. SSH client is almost in all Linux or Mac OS X distributions. You can use PuTTy SSH client in Windows. X11 server is part of all Linux distributions. Use XQuartz for Mac OS X. Use MobaXterm in Windows - which includes also SSH client, so PuTTy is nod needed, when using MobaXterm.
MobaXterm and Linux options worked best for me.
  - 3)Once you’ve been granted the access to SLURM, you can log in to via SSH client:
  
Address of the access node is: login.rci.cvut.cz (for older Intel nodes n01-n33) or login3.rci.cvut.cz (for newer AMD nodes a01-a16,g01-g12). So in Linux and Mac OS X run from terminal:
  
    ssh username@login.rci.cvut.cz
  
for command line access or

    ssh -X username@login.rci.cvut.cz

for X11 forwarding. MobaXterm automatically uses X11 forwarding when connecting to SSH host.

After logging in to your cluster run these commands:

Install miniconda (just to get a Python environment ready, not needed if there's already a Python environment up and running)
 
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh

    bash ~/Miniconda3-latest-Linux-x86_64.sh -b -p $HOME/miniconda

Start conda
 
    eval "$($HOME/miniconda/bin/conda shell.bash hook)"

Install ploomber in the base environment so we can download an example and submit the jobs

    pip install ploomber

Download sample pipeline to example/

    ploomber examples -n templates/ml-basic -o example
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
