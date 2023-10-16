# MLflow Tracking Server Stress Test

This folder contains three different stress tests for the MLflow Tracking Server:

1. [`increasing_number_of_requests.py`](./increasing_number_of_requests.py): Logs parameters and increases the number of parameters exponentially.

   Sends 10, 100, 1.000, 10.000 parameters using

   - `mlflow.log_param`
   - `mlflow.log_params`
   - `mlflow.log_batch`

   and saves the results as well as saves them to `results-parameters.csv`.

2. [`increasing_artifact_file_size`](./increasing_artifact_file_size.py): Logs artifacts from given folders that ideally have exponentially increasing size.

    The script assumes the data to be located in sub-folders at `$HOME/data/mlflow_server_stress_test` that
    are named

    - `1MB`
    - `10MB`
    - `100MB`
    - `1000MB`

    which should contain one file or multiple files that roughly add up to the respective size
    indicated by the folder name.

    Files of random size may e.g. be downloaded from [filesamples.com](https://filesamples.com/formats/mp4).

    The script then logs these artifacts with increasing size using

    - `mlflow.log_artifact`
    - `mlflow.log_artifacts`

   and saves the results as well as saves them to `results-artifacts.csv`.

3. [`increasing_number_of_parallel_runs.py`](./increasing_number_of_parallel_runs.py): Creates an exoponentially increasing number of parallel runs and logs parameters to them.

   Starts 10, 100, 1.000, 10.000 parallel runs and

   - logs parameters using `mlflow.log_params`
   - logs arficats using `mlflow.log_artifacts`

   and saves the results as well as saves them to `results-parallel-runs.csv`.

   The location of the artifacts is assumed to be the same as for 2., but it only uploads the `100MB` folder.

   **Note:** This test creates as many workers as parallel runs! Hence, it might crash your machine quickly. The tests were run on JUWELS Booster.

All scripts offer a CLI that allows to pass e.g.

- `--sleep-time`: defines the amount of seconds to sleep between each stress test step.

  This allows the server to restart in case of a crash.
- `--dry-run`:  allows to dry run, i.e. run the scripts without creating any runs or logging any parameters or artifacts.

## Required environment variables

All scripts require the following environment variables:

- `MLFLOW_TRACKING_URL`
- `MANTIK_USERNAME`
- `MANTIK_PASSWORD`
- `MLFLOW_EXPERIMENT_ID`

## Evaluation of the Stress  Tests

The Juptyer Notebook [`results.ipynb`](./results.ipynb) allows to read the CSV files of the results and plot them.
