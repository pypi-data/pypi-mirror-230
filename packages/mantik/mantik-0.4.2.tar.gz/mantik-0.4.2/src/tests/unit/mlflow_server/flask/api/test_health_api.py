import mantik.mlflow_server.flask.api.health as health


def test_health_check(
    client,
):
    response = client.get(health.HEALTH_CHECK_API_PATH)

    assert response.status_code == 200
