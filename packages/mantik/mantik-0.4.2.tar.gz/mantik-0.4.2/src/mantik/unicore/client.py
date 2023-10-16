import logging
import pathlib
import typing as t
import uuid

import pyunicore.client as pyunicore

import mantik.unicore._connect as _connect
import mantik.unicore.config.core as core
import mantik.unicore.credentials as _unicore_credentials
import mantik.unicore.exceptions as exceptions
import mantik.unicore.job as job_wrapper

logger = logging.getLogger(__name__)


class Client:
    def __init__(self, client: pyunicore.Client):
        self._client = client

    @classmethod
    def from_api_url_or_config(
        cls,
        api_url: t.Optional[str] = None,
        config: t.Optional[pathlib.Path] = None,
        connection_id: t.Optional[uuid.UUID] = None,
    ) -> "Client":
        """Create from API URL or config."""
        if api_url is not None:
            return cls.from_api_url(api_url, connection_id=connection_id)
        elif config is not None:
            return cls.from_config(config, connection_id=connection_id)
        raise ValueError(
            "The possible inputs are:\n"
            "- job_id and api-url\n"
            "- job_id and backend_config"
        )

    @classmethod
    def from_api_url(
        cls, url: str, connection_id: t.Optional[uuid.UUID] = None
    ) -> "Client":
        """Create from API URL."""
        unicore_credentials = (
            _unicore_credentials.UnicoreCredentials.get_credentials(
                connection_id
            )
        )
        client = _connect.create_unicore_api_connection(
            api_url=url,
            user=unicore_credentials.username,
            password=unicore_credentials.password,
        )
        return cls(client)

    @classmethod
    def from_config(
        cls, path: pathlib.Path, connection_id: t.Optional[uuid.UUID] = None
    ) -> "Client":
        """Create from backend config by reading its API URL."""
        config = core.Config.from_filepath(path, connection_id=connection_id)
        client = _connect.create_unicore_api_connection(
            api_url=config.api_url,
            user=config.user,
            password=config.password,
        )
        return cls(client)

    def get_job(self, job_id: str) -> job_wrapper.Job:
        """Get a job by ID."""
        for job in self.get_jobs():
            if job_id == job.id:
                return job
        raise exceptions.UnicoreError(f"No job with id {job_id} was found")

    def get_jobs(
        self, offset: int = 0, total: t.Optional[int] = None
    ) -> t.List[job_wrapper.Job]:
        """Get all UNICORE jobs deployed by the user.

        Parameters
        ----------
        offset : int, default=0
            List jobs starting at `offset`.
        total : int, optional
            Total number of jobs to list.

        """
        jobs = [
            job_wrapper.Job(job)
            for job in self._client.get_jobs(offset=offset, num=total)
        ]
        n_jobs = total or len(jobs) + 1
        return jobs[slice(0, n_jobs)]

    def submit_job(
        self,
        job_description: t.Dict,
        input_files: t.List[pathlib.Path],
        run_id: str,
    ) -> job_wrapper.Job:
        """Submit a job to UNICORE."""
        job = self._client.new_job(
            job_description=job_description,
            inputs=input_files,
        )
        job = _start_job(job=job, run_id=run_id)
        job = job_wrapper.Job(job)
        return job


def _start_job(job: pyunicore.Job, run_id: str) -> pyunicore.Job:
    job.start()
    logger.info(f"Started job {job.job_id} with run_id {run_id}")
    return job
