import mantik.compute_backend_service.models as models


def test_submit_run_response():
    response = models.SubmitRunResponse(
        experiment_id=1, run_id=2, unicore_job_id=3, tracking_uri="foo.bar"
    )
    assert response.experiment_id == 1
    assert response.run_id == "2"
    assert response.unicore_job_id == "3"
