import pathlib

import mlflow.entities as entities
import pytest

import mantik.testing.pyunicore as test_unicore
import mantik.unicore.properties as properties_wrapper
import mantik.unicore.working_dir as working_dir


class TestSubmittedUnicoreRun:
    def test_run_id(self, example_job_properties):
        run = test_unicore._create_run(properties=example_job_properties)
        expected = "test-job"

        result = run.run_id

        assert result == expected

    def test_properties(self, example_job_properties):
        run = test_unicore._create_run(
            status=properties_wrapper.Status.QUEUED,
            properties=example_job_properties,
        )
        example_job_properties.status = properties_wrapper.Status.QUEUED
        expected = example_job_properties

        result = run.properties

        assert result == expected

    def test_working_directory(self, example_job_properties):
        run = test_unicore._create_run(example_job_properties)

        working_directory = run.working_directory

        assert isinstance(working_directory, working_dir.WorkingDirectory)

    def test_logs(self, example_job_properties):
        example_job_properties.logs = ["test"]
        run = test_unicore._create_run(properties=example_job_properties)
        expected = ["test"]

        result = run.logs

        assert result == expected

    @pytest.mark.parametrize(
        ("will_be_successful", "expected"),
        [
            (
                True,
                True,
            ),
            (
                False,
                False,
            ),
        ],
    )
    def test_wait(self, will_be_successful, expected, example_job_properties):
        run = test_unicore._create_run(
            will_be_successful=will_be_successful,
            properties=example_job_properties,
        )
        result = run.wait()

        assert result == expected

    @pytest.mark.parametrize(
        ("status", "expected"),
        [
            (
                properties_wrapper.Status.STAGING_IN,
                entities.RunStatus.SCHEDULED,
            ),
            (
                properties_wrapper.Status.READY,
                entities.RunStatus.SCHEDULED,
            ),
            (
                properties_wrapper.Status.QUEUED,
                entities.RunStatus.SCHEDULED,
            ),
            (
                properties_wrapper.Status.RUNNING,
                entities.RunStatus.RUNNING,
            ),
            (
                properties_wrapper.Status.STAGING_OUT,
                entities.RunStatus.RUNNING,
            ),
            (
                properties_wrapper.Status.SUCCESSFUL,
                entities.RunStatus.FINISHED,
            ),
            (
                properties_wrapper.Status.FAILED,
                entities.RunStatus.FAILED,
            ),
            (
                properties_wrapper.Status.UNKNOWN,
                entities.RunStatus.RUNNING,
            ),
        ],
    )
    def test_get_status(self, status, expected, example_job_properties):
        run = test_unicore._create_run(
            status=status, properties=example_job_properties
        )
        result = run.get_status()

        assert result == expected

    def test_cancel(self, example_job_properties):
        run = test_unicore._create_run(properties=example_job_properties)

        run.cancel()

    def test_read_file_from_working_directory(self, example_job_properties):
        run = test_unicore._create_run(properties=example_job_properties)
        expected = "Stat stdout"

        result = run.read_file_from_working_directory(pathlib.Path("stdout"))

        assert result == expected
