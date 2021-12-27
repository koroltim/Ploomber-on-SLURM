

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
    cd ml-basic

Create the project's virtual env
 
    python -m venv ml-basic-env
    source ml-basic-env/bin/activate
    pip install -r requirements.txt

Copy submit.py (see source code in files) to ml-basic/submit.py, then submit to the cluster with:
  
    python submit.py
   
If all works, you'll see an ml-basic/output folder with:

    features.parquet
    get.parquet
    join.parquet
    Model.pickle
    nb.ipynb

