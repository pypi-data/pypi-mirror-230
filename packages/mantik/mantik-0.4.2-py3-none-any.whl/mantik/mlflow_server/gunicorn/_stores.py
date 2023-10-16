import argparse
import logging

import mlflow.server as server
import mlflow.utils.server_cli_utils as server_cli_utils

logger = logging.getLogger(__name__)


def initialize_backend_stores(args: argparse.Namespace) -> None:
    """Initialize the backend stores.

    Notes
    -----
    For reference see `mlflow.cli.server`.

    """
    if args.testing:
        return

    default_artifact_root = server_cli_utils.resolve_default_artifact_root(
        serve_artifacts=args.serve_artifacts,
        default_artifact_root=None,
        backend_store_uri=args.backend_store_uri,
    )
    logger.info(
        (
            "Initializing backend stores with backend store_uri=%s and"
            "default_artifact_root=%s"
        ),
        args.backend_store_uri,
        default_artifact_root,
    )
    server.handlers.initialize_backend_stores(
        backend_store_uri=args.backend_store_uri,
        default_artifact_root=default_artifact_root,
    )
