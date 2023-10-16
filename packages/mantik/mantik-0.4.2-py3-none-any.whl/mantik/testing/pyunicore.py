import datetime
import io
import typing as t

import pyunicore.client

import mantik.unicore as unicore
import mantik.unicore.job as job_wrapper
import mantik.unicore.properties as properties_wrapper
import mantik.unicore.submitted_run as submitted_run


class FakeTransport:
    def __init__(self, credential: str = "test_token", oidc: bool = True):
        self.credential = credential
        self.oidc = oidc


class FakeJob:
    def __init__(
        self,
        transport: FakeTransport,
        job_url: str = "test-job",
        properties: t.Dict = None,
        existing_files: t.Dict[str, str] = None,
        will_be_successful: bool = True,
        submission_day: int = 1,
    ):
        self.transport = transport
        self.url = job_url
        self._properties = properties or {
            "status": "SUCCESSFUL",
            "log": [],
            "owner": "owner",
            "siteName": "siteName",
            "consumedTime": {
                "total": 1,
                "queued": 2,
                "stage-in": 3,
                "preCommand": 4,
                "main": 5,
                "postCommand": 6,
                "stage-out": 7,
            },
            "currentTime": _format_datetime_str_with_time_zone(submission_day),
            "submissionTime": _format_datetime_str_with_time_zone(
                submission_day
            ),
            "terminationTime": _format_datetime_str_with_time_zone(
                submission_day + 1
            ),
            "statusMessage": "statusMessage",
            "tags": [],
            "resourceStatus": "resourceStatus",
            "name": "name",
            "exitCode": "0",
            "queue": "queue",
            "submissionPreferences": {},
            "resourceStatusMessage": "N/A",
            "acl": [],
            "batchSystemID": "N/A",
        }
        self._existing_files = existing_files or {}
        self._successful = will_be_successful
        self.working_dir = FakeWorkDir()
        self.started = False

    @property
    def properties(self) -> t.Dict:
        return self._properties

    @property
    def job_id(self) -> str:
        return self.url

    def poll(self) -> None:
        self._properties["status"] = (
            "SUCCESSFUL" if self._successful else "FAILED"
        )

    def abort(self) -> None:
        pass

    def start(self) -> None:
        self.started = True


def _format_datetime_str_with_time_zone(day: int) -> str:
    return datetime.datetime(
        2000,
        1,
        day,
        tzinfo=unicore.properties.TZ_OFFSET,
    ).strftime(unicore.properties.UNICORE_TIMESTAMP_FORMAT)


class FakeWorkDir:
    DEFAULT_FILES = ["stdout", "stderr", "mantik.log"]

    def __init__(self, files: t.Optional[t.List[str]] = None):
        self.directory = "."
        self._files = files or self.DEFAULT_FILES

    @property
    def properties(self):
        return {"foo": "bar"}

    def listdir(self, base="/"):
        return {
            f"{base}file1": FakeFileReference(content="File 1"),
            f"{base}file2": FakeFileReference(content="File 2"),
        }

    def stat(self, filename):
        if filename == "fake_dir":
            return FakeDirReference()
        if filename == "file_does_not_exist":
            raise FileNotFoundError()
        return FakeFileReference(content=f"Stat {filename}")


class FakeFileReference(pyunicore.client.PathFile):
    def __init__(self, content: str, name: str = "file"):
        self._content = content
        self.name = name

    def raw(self):
        return io.StringIO(self._content)

    def download(self, name: str) -> None:
        """we are not testing io, since unicore handels it"""
        pass


class FakeClient:
    def __init__(
        self,
        transport: FakeTransport = None,
        site_url: str = "test_api_url",
        login_successful: bool = False,
    ):
        if transport is None:
            transport = FakeTransport()
        self.transport = transport
        self.site_url = site_url
        self._properties = {"client": {"xlogin": {}}}
        if login_successful:
            self.add_login_info({"test_login": "test_logged_in"})

    @property
    def properties(self) -> t.Dict:
        return {**self.__dict__, **self._properties}

    def add_login_info(self, login: t.Dict) -> None:
        self._properties["client"]["xlogin"] = login

    def new_job(self, job_description: t.Dict, inputs: t.List) -> FakeJob:
        return FakeJob(transport=self.transport, job_url="test_job_url")

    def get_jobs(
        self, offset: int = 0, num: t.Optional[int] = None
    ) -> t.List[FakeJob]:
        total = (num or 10) + offset
        return [
            FakeJob(
                transport=self.transport,
                job_url=f"test_job_url{i}",
                submission_day=i + 1,
            )
            for i in range(total, offset - 1, -1)
        ]


class FakeDirReference(pyunicore.client.PathDir):
    def __init__(self, files: t.List[FakeFileReference] = []):
        self.storage = FakeWorkDir(files)
        self.name = "fakedir"


def _to_original_dict(d):
    return {
        "status": d.status.value,
        "log": d.logs,
        "owner": d.owner,
        "siteName": d.site_name,
        "consumedTime": {
            "total": str(d.consumed_time.total.seconds),
            "queued": str(d.consumed_time.queued.seconds),
            "stage-in": str(d.consumed_time.stage_in.seconds),
            "preCommand": str(d.consumed_time.pre_command.seconds),
            "main": str(d.consumed_time.main.seconds),
            "postCommand": str(d.consumed_time.post_command.seconds),
            "stage-out": str(d.consumed_time.stage_out.seconds),
        },
        "currentTime": d.current_time.isoformat(),
        "submissionTime": d.submission_time.isoformat(),
        "terminationTime": d.termination_time.isoformat(),
        "statusMessage": d.status_message,
        "tags": d.tags,
        "resourceStatus": d.resource_status,
        "name": d.name,
        "queue": d.queue,
        "submissionPreferences": d.submission_preferences,
        "exitCode": d.exit_code,
        "batchSystemID": d.batch_system_id,
        "resourceStatusMessage": d.resource_status_message,
        "acl": d.acl,
    }


def _create_run(
    properties: properties_wrapper.Properties,
    status: properties_wrapper.Status = None,
    will_be_successful: bool = True,
) -> submitted_run.SubmittedUnicoreRun:
    if status is not None:
        properties.status = status

    job = FakeJob(
        transport=FakeTransport(),
        job_url="test-job",
        properties=_to_original_dict(properties),
        will_be_successful=will_be_successful,
    )
    job = job_wrapper.Job(job)
    return submitted_run.SubmittedUnicoreRun(run_id="test-job", job=job)
