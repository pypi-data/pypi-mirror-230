import logging
import typing as t

import mantik.mlflow_server.flask.app as flask_app
import mantik.mlflow_server.gunicorn._app as gunicorn_app
import mantik.mlflow_server.gunicorn._cli_args as _cli_args


def _create_app(
    argv: t.Optional[t.List[str]] = None,
) -> gunicorn_app.MantikMlflowApplication:
    args = _cli_args.parse_args(argv)
    return gunicorn_app.MantikMlflowApplication.from_args(
        args=args, application=flask_app.app
    )


if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.DEBUG)

    app = _create_app()
    app.run()
