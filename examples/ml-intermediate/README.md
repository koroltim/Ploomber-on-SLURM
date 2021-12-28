

# Intermediate ML project

<!-- start description -->
Training and serving ML pipelines with integration testing to evaluate training data quality.
<!-- end description -->

## Training pipeline

The training pipeline prepares some data (`get`, `sepal-area`, `petal-area`), joins everything into a single file (`join`), and fits a model (`fit`). 

```python
from ploomber.spec import DAGSpec

dag_train = DAGSpec('pipeline.yaml').to_dag()
dag_train.plot()
```

## Serving pipeline

The serving pipeline gets data that we want to make predictions on, generates the same features we created during training, joins everything into a single file, and makes predictions using a previously trained model.

```python
dag_serve = DAGSpec('pipeline.serve.yaml').to_dag()
dag_serve.plot()
```

## Integration testing

This example also shows how to use integration testing to evaluate the quality of our data. The `join` task uses the `on_finish` hook, which allows us to run a function when the task finishes execution:

<!-- #md -->
```yaml
# Content of partial.features.yaml
  name: join
  product: "{{root}}/sample={{sample}}/join.parquet"
  on_finish: integration.no_missing_values
```
<!-- #endmd -->

The function checks that there are no missing values in the data frame. Otherwise, it raises an exception:

<!-- #md -->
```python
# Content of integration.py
import pandas as pd


def no_missing_values(product):
    df = pd.read_parquet(str(product))
    assert not df.isna().sum().sum(), f'Found missing values in {product}'

```
<!-- #endmd -->

# Running the example
Start conda
 
    eval "$($HOME/miniconda/bin/conda shell.bash hook)"

Install ploomber in the base environment so we can download an example and submit the jobs

    pip install ploomber

Download sample pipeline to ml-basic/

    ploomber examples -n templates/ml-intermediate -o ml-intermediate
    cd ml-intermediate

Create the project's virtual env
 
    python -m venv ml-intermediate-env
    source ml-intermediate-env/bin/activate
    pip install -r requirements.txt

To train the model copy train.py (see source code in files) to ml-intermediate/train.py, then submit it to the cluster with:
  
    python train.py


To serve the predictions of the model is trained copy serve.py(see source code in files) to ml-intermediate/serve.py, then submit it to the cluster with:

    python serve.py
    
    
If everything is done correctly, inside ml-intermediate/output/train/sample=False/ directory you should have these files:

      get.parquet  
      join.parquet  
      model.pickle  
      nb.html  
      petal_area.parquet  
      sepal_area.parquet

