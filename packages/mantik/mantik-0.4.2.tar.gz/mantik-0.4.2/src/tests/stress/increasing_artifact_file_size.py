import dataclasses
import itertools
import logging
import os
import pathlib
import time
import typing as t

import mlflow.entities
import pandas as pd

import mantik
import mantik.testing.stress as stress


logger = logging.getLogger()
stress.setup_logger(logger)


@dataclasses.dataclass
class Results(stress.ResultsBase):
    total_size: int
    n_files: int
    duration_per_file: float = None
    duration_per_mb: float = None

    def __post_init__(self):
        self.duration_per_file = self.duration / self.n_files
        self.duration_per_mb = self.duration / self.total_size
        logger.info(
            (
                "Sending %s files with total size %s MB via "
                "mlflow.%s %s %s seconds, "
                "average duration per MB was %s seconds, "
                "average duration per file was %s seconds, "
            ),
            self.n_files,
            self.total_size,
            self.mlflow_method,
            "failed after" if self.failed else "succeeded in",
            self.duration,
            self.duration_per_mb,
            self.duration_per_file,
        )

    def to_table_row(self) -> str:
        return (
            f"| {self.total_size} "
            f"| {self.n_files} "
            f"| {self.mlflow_method} "
            f"| {self.duration} "
            f"| {self.duration_per_mb} "
            f"| {self.duration_per_file} "
            f"| {not self.failed} "
            f"|\n"
        )

    def insert_to_df(self, df: pd.DataFrame) -> None:
        row = df.loc[self.total_size, self.mlflow_method]
        row["duration"] = self.duration
        row["duration per file"] = self.duration_per_file
        row["duration per MB"] = self.duration_per_mb
        row["succeeded"] = not self.failed


def run_stress_test(sleep_time: int, dry_run: bool = False):
    results = []
    home = os.getenv("HOME")
    base_dir = pathlib.Path(f"{home}/data/mlflow_server_stress_test")
    values = [1, 10, 100, 1000]
    paths = [
        base_dir / "1MB",
        base_dir / "10MB",
        base_dir / "100MB",
        base_dir / "1000MB",
    ]

    methods = ["log_artifact", "log_artifacts"]

    index = pd.MultiIndex.from_arrays(
        list(zip(*itertools.product(values, methods))),
        names=["total size [MB]", "method"],
    )

    df = pd.DataFrame(
        data=None,
        index=index,
        columns=[
            "duration",
            "duration per MB",
            "duration per file",
            "succeeded",
        ],
    )

    context = stress.get_context(dry_run)

    for total_size, path in zip(values, paths):
        for method in [
            _log_individual_artifacts_for_run,
            _log_grouped_artifacts_for_run,
        ]:
            logger.info(
                "Running test for logging %s MB via %s",
                total_size,
                method.__name__,
            )
            result = method(
                total_size=total_size,
                path=path,
                dry_run=dry_run,
                context=context,
            )
            result.insert_to_df(df)
            results.append(result)
            logger.info(
                "Sleeping for %s seconds until next stress test", sleep_time
            )
            time.sleep(sleep_time)
    df.to_csv("results-artifacts.csv")
    logger.info("Results saved to results-artifacts.csv")
    stress.log_results(
        results,
        columns=[
            "total size [MB]",
            "# files",
            "method",
            "duration",
            "duration per MB",
            "duration per file",
            "succeeded",
        ],
        logger=logger,
    )


def _log_results(results: t.List[Results]) -> None:
    rows = [result.to_table_row() for result in results]
    table = "|  |\n" "| --- | --- | --- | --- | --- | --- |\n" + "".join(rows)
    logger.info("Stress test results: \n%s", table)


def _log_individual_artifacts_for_run(
    total_size: int, path: pathlib.Path, dry_run: bool, context: stress.Context
) -> Results:
    failed = False
    files = list(path.glob("*"))
    n_files = len(files)
    start = time.time()
    with context(run_name=f"test-requests-individual-{total_size}-MB"):
        for i, file in enumerate(files):
            try:
                if not dry_run:
                    mlflow.log_artifact(file.as_posix(), f"test-file-{i}.mp4")
            except:  # noqa: E722
                logger.exception(
                    "Exception after %s individual artifacts", i, exc_info=True
                )
                failed = True
                break
    duration = time.time() - start
    return Results(
        total_size=total_size,
        n_files=n_files,
        mlflow_method="log_artifact",
        duration=duration,
        failed=failed,
    )


def _log_grouped_artifacts_for_run(
    total_size: int,
    path: pathlib.Path,
    dry_run: bool,
    context: stress.Context,
) -> Results:
    failed = False
    files = list(path.glob("*"))
    n_files = len(files)
    start = time.time()
    with context(run_name=f"test-requests-grouped-{total_size}-MB"):
        try:
            if not dry_run:
                mlflow.log_artifacts(path.as_posix())
        except:  # noqa: E722
            logger.exception(
                "Exception sending %s MB grouped artifacts",
                total_size,
                exc_info=True,
            )
            failed = True
    duration = time.time() - start
    return Results(
        total_size=total_size,
        n_files=n_files,
        mlflow_method="log_artifacts",
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
