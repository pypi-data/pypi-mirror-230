import fastapi

import mantik.compute_backend_service.app as _app
import mantik.compute_backend_service.exceptions as _exceptions


def test_create_app():
    global_path_prefix = "/fizzbuzz"
    docs_url = "/foo"
    app = _app.create_app(
        docs_url=docs_url,
        redoc_url="/bar",
        openapi_url="/baz.json",
        global_path_prefix=global_path_prefix,
    )
    assert isinstance(app, fastapi.FastAPI)
    route_paths = [route.path for route in app.routes]
    assert f"{global_path_prefix}/submit/{{experiment_id}}" in route_paths
    assert global_path_prefix + docs_url in route_paths
    exception_handlers = app.exception_handlers
    assert _exceptions.unicore_exception_handler in exception_handlers.values()
