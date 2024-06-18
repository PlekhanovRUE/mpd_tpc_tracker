# Start searching for parameters

1) Installing the necessary libraries

If there is no virtual environment created:
```shell
python3 -m venv venv
```

If a virtual environment has already been created, you need to activate it:
```shell
source venv/bin/activate
```

Installing libraries:
```shell
pip install optuna
pip install optuna-integration
pip install botorch
```
2) Running the script:

```shell
python3 param_optimize/black-box-opt.py
```

# Script parameters that can be varied:
* **NUM_TRIALS** - the number of “epochs”, that is, the number of calls to the target function;
* **sampler** - select an algorithm for searching for hyperparameters;
* **LOG_DIR** - directory for saving hyperparameter search logs.