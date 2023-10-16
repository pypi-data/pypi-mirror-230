import argparse
import logging
import multiprocessing
import typing as t


def create_gunicorn_options(args: argparse.Namespace) -> t.Dict:
    """Create the options for the gunicorn app."""
    number_of_workers = _number_of_workers()
    logging.info(f"Creating Gunicorn application with {number_of_workers}")
    return {
        "bind": f"{args.host}:{args.port}",
        "workers": number_of_workers,
        "loglevel": "debug",
        "max_requests": "1000",
        "max_requests_jitter": "100",
    }


def _number_of_workers() -> int:
    return (multiprocessing.cpu_count() * 2) + 1
