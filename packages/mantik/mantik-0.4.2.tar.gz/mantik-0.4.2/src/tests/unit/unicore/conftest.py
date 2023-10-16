import datetime
import json
import pathlib

import pytest

import mantik.unicore as unicore
import mantik.unicore.config as config
import mantik.unicore.config.executable as executable
import mantik.unicore.properties as properties

FILE_DIR = pathlib.Path(__file__).parent


@pytest.fixture(scope="function")
def example_config() -> config.core.Config:
    return config.core.Config(
        api_url="test-url",
        user="user",
        password="password",
        project="test-project",
        environment=config.environment.Environment(
            execution=executable.Apptainer(
                path=pathlib.Path("mantik-test.sif"),
            ),
            variables={"SRUN_CPUS_PER_TASK": 100},
        ),
        resources=config.resources.Resources(queue="batch"),
        exclude=["*.py", "*.sif"],
    )


@pytest.fixture()
def example_job_property_response() -> dict:
    with open(
        FILE_DIR
        / "../../resources/unicore-responses/job-property-response.json",
    ) as f:
        return json.load(f)


@pytest.fixture()
def example_job_properties():
    return properties.Properties(
        status=properties.Status.SUCCESSFUL,
        logs=[],
        owner="owner",
        site_name="siteName",
        consumed_time=properties.ConsumedTime(
            total=datetime.timedelta(seconds=1),
            queued=datetime.timedelta(seconds=2),
            stage_in=datetime.timedelta(seconds=3),
            pre_command=datetime.timedelta(seconds=4),
            main=datetime.timedelta(seconds=5),
            post_command=datetime.timedelta(seconds=6),
            stage_out=datetime.timedelta(seconds=7),
        ),
        current_time=datetime.datetime(
            2000, 1, 1, tzinfo=unicore.properties.TZ_OFFSET
        ),
        submission_time=datetime.datetime(
            2000, 1, 1, tzinfo=unicore.properties.TZ_OFFSET
        ),
        termination_time=datetime.datetime(
            2000, 1, 2, tzinfo=unicore.properties.TZ_OFFSET
        ),
        status_message="statusMessage",
        tags=["tag"],
        resource_status="resourceStatus",
        name="name",
        exit_code="0",
        queue="queue",
        submission_preferences={"any": "preferences"},
        resource_status_message="resourceStatusMessage",
        acl=["acl"],
        batch_system_id="batchSystemID",
    )


@pytest.fixture()
def example_config_for_python() -> config.core.Config:
    return config.core.Config(
        api_url="test-url",
        user="user",
        password="password",
        project="test-project",
        environment=config.environment.Environment(
            execution=executable.Python(
                path=pathlib.Path("/venv"),
            )
        ),
        resources=config.resources.Resources(queue="batch"),
        exclude=["*.sif"],
    )
