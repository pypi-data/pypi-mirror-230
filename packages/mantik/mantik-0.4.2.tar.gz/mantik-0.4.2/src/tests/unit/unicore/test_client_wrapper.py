import pytest

import mantik.testing.pyunicore as testing
import mantik.unicore.client as _client
import mantik.unicore.exceptions as exceptions


@pytest.fixture()
def client():
    return _client.Client(testing.FakeClient())


class TestClient:
    def test_get_non_existing_job(self, client):
        job_id = "this_id_does_not_exists"
        with pytest.raises(exceptions.UnicoreError) as e:
            client.get_job(job_id)
            assert e.value == f"No job with id {job_id} was found"

    def test_get_job(self, client):
        job_id = "test_job_url0"
        result = client.get_job(job_id)
        assert result.id == job_id

    @pytest.mark.parametrize(
        ("offset", "total", "expected"),
        [
            # testing.pyunicore.FakeClient.get_jobs creates 10 jobs with
            # IDs 10 to 0 and submission times day 11 to 1.
            (0, None, range(10, -1, -1)),
            (2, None, range(12, 1, -1)),
            (2, 5, range(7, 3, -1)),
        ],
    )
    def test_get_jobs(self, client, offset, total, expected):
        result = client.get_jobs(offset=offset, total=total)

        for res, exp in zip(result, expected):
            assert res.id == f"test_job_url{exp}"
