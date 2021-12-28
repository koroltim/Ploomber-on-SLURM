
Currently doesn't work on SLURM,need to rewrite the submission script
<!-- start header -->
To run this example locally execute: `ploomber examples -n templates/ml-advanced`

<!-- end header -->


# ML advanced

<!-- start description -->
ML pipeline using the Python API. Shows how to create a Python package, test it with pytest, and train models in parallel.
<!-- end description -->

## Build

```sh
ploomber build --entry-point ml_advanced.pipeline.make
```

## Testing

```bash
# complete (force execution of all tasks)
pytest --force
```

```bash
# incremental (will only run the tasks that have changed)
pytest
```
