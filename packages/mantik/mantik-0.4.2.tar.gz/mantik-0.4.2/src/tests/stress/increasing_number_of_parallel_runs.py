import asyncio
import concurrent.futures as futures
import dataclasses
import itertools
import logging
import os
import pathlib
import time

import mlflow.entities
import pandas as pd

import mantik
import mantik.testing.stress as stress

logger = logging.getLogger()
stress.setup_logger(logger)

N_PARAMS = 50


@dataclasses.dataclass
class Results(stress.ResultsBase):
    n_parallel_runs: int
    duration_per_param: float = None

    def __post_init__(self):
        self.duration_per_param = self.duration / self.n_parallel_runs
        logger.info(
            (
                "Sending %s params via mlflow.%s to %s parallel runs "
                "%s %s seconds, "
                "average duration per param was %s seconds"
            ),
            N_PARAMS,
            self.mlflow_method,
            self.n_parallel_runs,
            "failed after" if self.failed else "succeeded in",
            self.duration,
            self.duration_per_param,
        )

    def to_table_row(self) -> str:
        return (
            f"| {self.n_parallel_runs} "
            f"| {self.mlflow_method} "
            f"| {self.duration} "
            f"| {self.duration_per_param} "
            f"| {not self.failed} "
            f"|\n"
        )

    def insert_to_df(self, df: pd.DataFrame) -> None:
        row = df.loc[self.n_parallel_runs, self.mlflow_method]
        row["duration"] = self.duration
        row["duration per param"] = self.duration_per_param
        row["succeeded"] = not self.failed


async def run_stress_test(loop, sleep_time: int, dry_run: bool = False):
    values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 100, 1000, 10000]
    methods = ["log_params"]
    index = pd.MultiIndex.from_arrays(
        list(zip(*itertools.product(values, methods))),
        names=["# parallel runs", "method"],
    )
    home = os.getenv("HOME")
    artifacts = pathlib.Path(f"{home}/data/mlflow_server_stress_test/100MB")

    df = pd.DataFrame(
        data=None,
        index=index,
        columns=["duration", "duration per param", "succeeded"],
    )

    context = stress.get_context(dry_run)

    results = []

    for n_parallel_runs in values:
        for method in methods:
            logger.info(
                "Running test for logging to %s parallel runs via %s",
                n_parallel_runs,
                method,
            )
            start = time.time()

            executor = futures.ProcessPoolExecutor(max_workers=n_parallel_runs)

            await asyncio.gather(
                *(
                    loop.run_in_executor(
                        executor,
                        _log_params_for_run,
                        n_parallel_runs,
                        N_PARAMS,
                        artifacts,
                        dry_run,
                        context,
                    )
                    for _ in range(n_parallel_runs)
                )
            )

            duration = time.time() - start
            result = Results(
                n_parallel_runs=n_parallel_runs,
                mlflow_method="log_params",
                duration=duration,
                failed=False,
            )
            result.insert_to_df(df)
            results.append(result)
            logger.info(
                "Sleeping for %s seconds until next stress test", sleep_time
            )
            time.sleep(sleep_time)
    df.to_csv("results-parallel-runs.csv")
    logger.info("Results saved to results-parallel-runs.csv")
    stress.log_results(
        results,
        columns=[
            "# parallel runs",
            "method",
            "duration",
            "duration per param",
            "succeeded",
        ],
        logger=logger,
    )


def _log_params_for_run(
    n_parallel_runs: int,
    n_params: int,
    artifacts: pathlib.Path,
    dry_run: bool,
    context: stress.Context,
) -> None:
    logger.info("Logging %s params and artifacts from %s", n_params, artifacts)
    params = {f"param-{i}": 1 for i in range(n_params)}
    with context(run_name=f"test-requests-grouped-{n_params}"):
        try:
            if not dry_run:
                mlflow.log_params(params)
                mlflow.log_artifacts(artifacts.as_posix())
        except:  # noqa: E722
            logger.exception(
                "Exception sending %s grouped params for %s parallel runs",
                n_params,
                n_parallel_runs,
                exc_info=True,
            )


if __name__ == "__main__":
    mantik.init_tracking()
    args = stress.setup_argpaser().parse_args()
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        run_stress_test(
            loop, sleep_time=int(args.sleep_time), dry_run=args.dry_run
        )
    )
