import flask
import pytest

import mantik.mlflow_server.flask.app as flask_app
import mantik.mlflow_server.tokens.verifier as verifier
import mantik.testing as testing


@pytest.fixture()
def app(monkeypatch) -> flask.Flask:
    monkeypatch.setattr(
        verifier,
        "TokenVerifier",
        testing.mlflow_server.FakeTokenVerifier,
    )

    _app = flask_app.app
    _app.config.update(
        {
            "TESTING": True,
        }
    )

    yield _app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def api_path() -> str:
    return "/api/2.0/mlflow"
