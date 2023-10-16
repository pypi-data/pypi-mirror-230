import datetime
import json
import pathlib
import typing as t

import pyunicore.client as pyunicore
import yaml

import mantik.unicore.exceptions as exceptions
import mantik.unicore.properties as properties
import mantik.unicore.working_dir as working_dir

APPLICATION_LOGS_FILE = "mantik.log"


class Job:
    """Job submitted to unicore, wrapper class around pyunicore.client.Job"""

    def __init__(self, job: pyunicore.Job):
        self._job = job

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"id={self.id}, "
            f"submitted_at={self.submitted_at}, "
            f"queue={self.queue}, "
            f"status={self.status.value})"
        )

    @property
    def id(self) -> str:
        """Return the job's UNICORE ID."""
        return self._job.job_id

    @property
    def status(self) -> properties.Status:
        """Return the job status."""
        return self.properties.status

    @property
    def queue(self) -> str:
        """Return the queue the job was submitted to."""
        return self.properties.queue

    @property
    def submitted_at(self) -> datetime.datetime:
        """Return when the job was submitted."""
        return self.properties.submission_time

    @property
    def properties(self) -> properties.Properties:
        """Return the job properties."""
        # This property might change with time.
        # Accessing pyunicore.client.Job.properties sends a request
        # at each call and caches the result for a certain amount of time.
        return properties.Properties.from_dict(self._job.properties)

    @property
    def unicore_logs(self) -> t.List[str]:
        """Return the UNICORE logs of the job."""
        logs = self.properties.logs
        return logs

    @property
    def application_logs(self) -> str:
        """Return the logs of the executed application."""
        try:
            application_logs = self.working_directory.get_directory_or_file(
                pathlib.Path(APPLICATION_LOGS_FILE)
            )
        except FileNotFoundError as e:
            if f"{APPLICATION_LOGS_FILE} does not exist" in str(e):
                raise exceptions.UnicoreError(
                    "Job not yet executed or failed, check job status "
                    "(see `mantik runs info --help`)"
                ) from e
            raise e
        return application_logs.content

    @property
    def working_directory(self) -> working_dir.WorkingDirectory:
        """Get the UNICORE working directory of the job."""
        return working_dir.WorkingDirectory(self._job.working_dir)

    def wait(self):
        """Wait until the job is finished."""
        self._job.poll()

    def cancel(self):
        """Cancel the job."""
        self._job.abort()

    def download(
        self,
        remote_path: pathlib.Path,
        local_path: pathlib.Path,
    ) -> None:
        """Download a file or folder from the working directory."""
        file_or_dir = self.working_directory.get_directory_or_file(remote_path)
        file_or_dir.download(local_path)

    def download_all(
        self,
        local_path: pathlib.Path,
    ) -> None:
        """Download a file or folder from the working directory."""
        storage = self.working_directory.get_entire_storage()
        for file in storage:
            file.download(local_path)

    def to_dict(self) -> t.Dict:
        return {
            "id": self.id,
            **self.properties.to_dict(),
        }

    def to_json(self) -> str:
        """Format as indented JSON string."""
        return json.dumps(self.to_dict(), indent=2)

    def to_yaml(self) -> str:
        """Format as indented YAML string."""
        return yaml.dump(self.to_dict(), default_flow_style=False)
