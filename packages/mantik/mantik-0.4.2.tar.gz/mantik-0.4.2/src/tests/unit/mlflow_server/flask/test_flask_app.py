import pytest


def test_authenticate_api_calls_returns_200_for_non_api_path(client, api_path):
    response = client.get("/#/experiments/0")

    assert response.status_code == 200


@pytest.mark.parametrize(
    ("headers", "expected_status_code", "expected_message"),
    [
        ({}, 401, "'Authorization' header missing"),
        ({"Authorization": ""}, 401, "Empty token in 'Authorization' header"),
        ({"Authorization": "test-invalid-token"}, 401, "Invalid token"),
        ({"Authorization": "Bearer test-invalid-token"}, 401, "Invalid token"),
        (
            {"Authorization": "test-valid-token"},
            200,
            None,
        ),
        ({"Authorization": "Bearer test-valid-token"}, 200, None),
    ],
)
def test_authenticate_api_calls(
    client, api_path, headers, expected_status_code, expected_message
):
    response = client.get(
        f"{api_path}/experiments/get",
        headers=headers,
        json={"experiment_id": 0},
    )

    assert response.status_code == expected_status_code
    if expected_message is not None:
        assert response.text == expected_message
