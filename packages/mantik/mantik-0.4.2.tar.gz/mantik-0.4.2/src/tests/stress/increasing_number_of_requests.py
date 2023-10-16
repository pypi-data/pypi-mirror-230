import dataclasses
import itertools
import logging
import time

import mlflow.entities
import pandas as pd

import mantik
import mantik.testing.stress as stress

logger = logging.getLogger()
stress.setup_logger(logger)


@dataclasses.dataclass
class Results(stress.ResultsBase):
    n_params: int
    duration_per_param: float = None

    def __post_init__(self):
        self.duration_per_param = self.duration / self.n_params
        logger.info(
            (
                "Sending %s params via mlflow.%s %s %s seconds, "
                "average duration per param was %s seconds"
            ),
            self.n_params,
            self.mlflow_method,
            "failed after" if self.failed else "succeeded in",
            self.duration,
            self.duration_per_param,
        )

    def to_table_row(self) -> str:
        return (
            f"| {self.n_params} "
            f"| {self.mlflow_method} "
            f"| {self.duration} "
            f"| {self.duration_per_param} "
            f"| {not self.failed} "
            f"|\n"
        )

    def insert_to_df(self, df: pd.DataFrame) -> None:
        row = df.loc[self.n_params, self.mlflow_method]
        row["duration"] = self.duration
        row["duration per param"] = self.duration_per_param
        row["succeeded"] = not self.failed


def run_stress_test(sleep_time: int, dry_run: bool = False):
    results = []

    values = [10, 100, 1000, 10000]
    methods = ["log_param", "log_params", "log_batch"]
    index = pd.MultiIndex.from_arrays(
        list(zip(*itertools.product(values, methods))),
        names=["# params", "method"],
    )

    df = pd.DataFrame(
        data=None,
        index=index,
        columns=["duration", "duration per param", "succeeded"],
    )

    context = stress.get_context(dry_run)

    for n_params in values:
        for method in [
            _log_individual_params_for_run,
            _log_grouped_params_for_run,
            _log_batched_params_for_run,
        ]:
            logger.info(
                "Running test for logging %s params via %s",
                n_params,
                method.__name__,
            )
            result = method(n_params=n_params, dry_run=dry_run, context=context)
            result.insert_to_df(df)
            results.append(result)
            logger.info(
                "Sleeping for %s seconds until next stress test", sleep_time
            )
            time.sleep(sleep_time)
    df.to_csv("results-parameters.csv")
    logger.info("Results saved to results-parameters.csv")
    stress.log_results(
        results,
        columns=[
            "# params",
            "method",
            "duration",
            "duration per param",
            "succeeded",
        ],
        logger=logger,
    )


def _log_individual_params_for_run(
    n_params: int,
    dry_run: bool,
    context: stress.Context,
) -> Results:
    failed = False
    start = time.time()
    with context(run_name=f"test-requests-individual-{n_params}"):
        for i in range(n_params):
            try:
                if not dry_run:
                    mlflow.log_param(key=f"param-{i}", value=1)
            except:  # noqa: E722
                logger.exception(
                    "Exception after %s individual params", i, exc_info=True
                )
                failed = True
                break
    duration = time.time() - start
    return Results(
        n_params=n_params,
        mlflow_method="log_param",
        duration=duration,
        failed=failed,
    )


def _log_grouped_params_for_run(
    n_params: int,
    dry_run: bool,
    context: stress.Context,
) -> Results:
    failed = False
    params = {f"param-{i}": 1 for i in range(n_params)}
    start = time.time()
    with context(run_name=f"test-requests-grouped-{n_params}"):
        try:
            if not dry_run:
                mlflow.log_params(params)
        except:  # noqa: E722
            logger.exception(
                "Exception sending %s grouped params", n_params, exc_info=True
            )
            failed = True
    duration = time.time() - start
    return Results(
        n_params=n_params,
        mlflow_method="log_params",
        duration=duration,
        failed=failed,
    )


def _log_batched_params_for_run(
    n_params: int, dry_run: bool, context: stress.Context
) -> Results:
    failed = False
    params = [
        mlflow.entities.Param(key=f"param-{i}", value=str(1))
        for i in range(n_params)
    ]
    start = time.time()
    with context(run_name=f"test-requests-grouped-{n_params}") as run:
        client = mlflow.MlflowClient()
        try:
            if not dry_run:
                client.log_batch(run_id=run.info.run_id, params=params)
        except:  # noqa: E722
            logger.exception(
                "Exception sending %s batched params", n_params, exc_info=True
            )
            failed = True
    duration = time.time() - start
    return Results(
        n_params=n_params,
        mlflow_method="log_batch",
        duration=duration,
        failed=failed,
    )


if __name__ == "__main__":
    mantik.init_tracking()
    args = stress.setup_argpaser().parse_args()
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    run_stress_test(sleep_time=int(args.sleep_time), dry_run=args.dry_run)
