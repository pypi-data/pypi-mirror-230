import abc
import argparse
import contextlib
import dataclasses
import logging
import typing as t

import mlflow


@contextlib.contextmanager
def dry_run_context(*args, **kwargs):
    yield


Context = t.Union[mlflow.start_run, dry_run_context]


def setup_logger(logger: logging.Logger) -> None:
    formatter = logging.Formatter(
        "%(asctime)s.%(msecs)03d %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logger.handlers[0].setFormatter(formatter)


@dataclasses.dataclass
class ResultsBase(abc.ABC):
    mlflow_method: str
    duration: float
    failed: bool

    @abc.abstractmethod
    def to_table_row(self) -> str:
        raise NotImplementedError


def setup_argpaser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="MLflow Tracking Server Stress Tests",
        description="""Runs stress tests against the MLflow Tracking Server.

        Logs 10, 100, 1000, and 10000 and parameters

        1. as individual calls of `mlflow.log_param`
        2. as one call of `mlflow.log_params` with all parameters
        3. as one call of `mlflow.MlflowClient.log_batch` with all parameters

        and prints the result of each test.

        """,
    )
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("-s", "--sleep-time", default=120)
    parser.add_argument("-d", "--dry-run", action="store_true")
    return parser


def get_context(dry_run: bool) -> contextlib.contextmanager:
    return mlflow.start_run if not dry_run else dry_run_context


def log_results(
    results: t.List[ResultsBase],
    columns: t.Iterable[str],
    logger: logging.Logger,
) -> None:
    rows = [result.to_table_row() for result in results]
    header = f"| {' | '.join(columns)} |\n"
    separator = f"| {' | '.join('---' for _ in columns)} |\n"
    table = "".join([header, separator, *rows])
    logger.info("Stress test results: \n%s", table)
