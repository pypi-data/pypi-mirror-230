import logging
import pathlib
import typing as t

import mlflow.entities as entities
import mlflow.projects as projects

import mantik.unicore.job as job
import mantik.unicore.properties as properties
import mantik.unicore.working_dir as working_dir

logger = logging.getLogger(__name__)


class SubmittedUnicoreRun(projects.SubmittedRun):
    """A run that was submitted through the UNICORE interface.

    This class encapsulates a UNICORE job.

    Parameters
    ----------
    run_id : str
        MLflow run ID.
    job : pyunicore.client.Job
        The UNICORE job.

    """

    def __init__(self, run_id: str, job: job.Job):
        self._id = run_id
        self._job = job

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"run_id={self.run_id}, "
            f"job={self.job_id}"
            ")"
        )

    @property
    def _status(self) -> properties.Status:
        status = self._job.properties.status
        logger.debug(f"UNICORE status of {self} is {status.value}")
        return status

    @property
    def job_id(self) -> str:
        return self._job.id

    @property
    def properties(self) -> properties.Properties:
        """Return the UNICORE job properties."""
        properties = self._job.properties
        logger.debug(f"Job properties for {self}: {properties}")
        return properties

    @property
    def working_directory(self) -> working_dir.WorkingDirectory:
        """Return the UNICORE working directory of the job."""
        return self._job.working_directory

    @property
    def logs(self) -> t.List[str]:
        """Return the UNICORE job logs."""
        return self._job.unicore_logs

    @property
    def run_id(self) -> str:
        """Return the run's ID."""
        return self._id

    def wait(self) -> bool:
        """Wait for the run to finish.

        Returns
        -------
        bool
            `True` if the run has finished successfully, `False` otherwise.

        """
        logger.info(f"Waiting for {self} to finish")
        self._job.wait()
        return self._status == properties.Status.SUCCESSFUL

    def get_status(self) -> entities.RunStatus:
        """Return the status of the run."""
        status = properties.MLFLOW_STATUS_MAPPING[self._status]
        logger.debug(f"Status of {self} is {status}")
        return status

    def cancel(self) -> None:
        """Cancel the run and wait until it was successfully terminated."""
        logger.debug(f"Cancelling UNICORE job for {self}")
        self._job.cancel()

    def read_file_from_working_directory(self, filename: pathlib.Path) -> str:
        """Read a file from the job's working directory."""
        logger.debug(f"Reading '{filename}' from working directory of {self}")
        file = self.working_directory.get_directory_or_file(filename)
        return file.content
