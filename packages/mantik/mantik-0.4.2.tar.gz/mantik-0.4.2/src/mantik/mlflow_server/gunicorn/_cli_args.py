import argparse
import typing as t


def parse_args(argv: t.Optional[t.List[str]] = None) -> argparse.Namespace:
    """Parse MLflow CLI args."""
    parser = argparse.ArgumentParser(
        description="Run the wrapped MLflow server."
    )
    parser.add_argument(
        "--host", type=str, default="0.0.0.0", help="Server host"
    )
    parser.add_argument("--port", type=int, default=8080, help="Server port")
    parser.add_argument(
        "--backend-store-uri", type=str, default=None, help="Backend store URI"
    )
    parser.add_argument(
        "--artifacts-destination",
        type=str,
        default=None,
        help="Artifacts destination URI",
    )
    parser.add_argument("--serve-artifacts", action="store_true", default=False)
    parser.add_argument("--testing", action="store_true", default=False)
    args = parser.parse_args(argv)
    return args
