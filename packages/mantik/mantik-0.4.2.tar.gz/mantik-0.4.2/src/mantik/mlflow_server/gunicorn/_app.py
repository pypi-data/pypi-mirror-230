import argparse
import typing as t

import flask
import gunicorn.app.base as base

import mantik.mlflow_server.gunicorn._env as _env
import mantik.mlflow_server.gunicorn._options as _options
import mantik.mlflow_server.gunicorn._stores as _stores


class MantikMlflowApplication(base.BaseApplication):
    """Gunicorn standalone application."""

    def __init__(
        self, application: flask.Flask, options: t.Optional[t.Dict] = None
    ):
        self.options = options or {}
        self.application = application
        super().__init__()

    @classmethod
    def from_args(
        cls, args: argparse.Namespace, application: flask.Flask
    ) -> "MantikMlflowApplication":
        _stores.initialize_backend_stores(args)
        _env.set_required_env_vars(args)
        options = _options.create_gunicorn_options(args)
        return cls(application=application, options=options)

    def init(self, parser, opts, args):
        pass

    def load_config(self):
        config = {
            key: value
            for key, value in self.options.items()
            if key in self.cfg.settings and value is not None
        }
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application
