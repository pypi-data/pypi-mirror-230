import argparse
import os

import mlflow.server as server


def set_required_env_vars(args: argparse.Namespace) -> None:
    """Set the required environment variables.

    Notes
    -----
    For reference see `mlflow.server._run_server`.

    """
    if args.backend_store_uri is not None:
        os.environ[server.BACKEND_STORE_URI_ENV_VAR] = args.backend_store_uri
    if args.artifacts_destination is not None:
        os.environ[
            server.ARTIFACTS_DESTINATION_ENV_VAR
        ] = args.artifacts_destination
    if args.serve_artifacts:
        os.environ[server.SERVE_ARTIFACTS_ENV_VAR] = "true"
