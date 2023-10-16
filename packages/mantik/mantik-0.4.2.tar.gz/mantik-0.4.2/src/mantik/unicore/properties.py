import dataclasses
import datetime
import enum
import typing as t

import mlflow.entities as entities

UNICORE_TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S%z"
TZ_OFFSET = datetime.timezone(datetime.timedelta(seconds=7200))
TIMESTAMP_STR_LENGTH = len(
    datetime.datetime(2000, 1, 1, tzinfo=TZ_OFFSET).strftime(
        UNICORE_TIMESTAMP_FORMAT
    )
)


class Status(enum.Enum):
    """Job statuses returned by the UNICORE API."""

    STAGING_IN = "STAGING_IN"
    READY = "READY"
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    STAGING_OUT = "STAGING_OUT"
    SUCCESSFUL = "SUCCESSFUL"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"

    def __len__(self) -> int:
        return len(self.value)


MLFLOW_STATUS_MAPPING = {
    Status.STAGING_IN: entities.RunStatus.SCHEDULED,
    Status.READY: entities.RunStatus.SCHEDULED,
    Status.QUEUED: entities.RunStatus.SCHEDULED,
    Status.RUNNING: entities.RunStatus.RUNNING,
    Status.STAGING_OUT: entities.RunStatus.RUNNING,
    Status.SUCCESSFUL: entities.RunStatus.FINISHED,
    Status.FAILED: entities.RunStatus.FAILED,
    Status.UNKNOWN: entities.RunStatus.RUNNING,
}


@dataclasses.dataclass
class ConsumedTime:
    """Consumed time of a job."""

    total: t.Optional[datetime.timedelta] = None
    queued: t.Optional[datetime.timedelta] = None
    stage_in: t.Optional[datetime.timedelta] = None
    pre_command: t.Optional[datetime.timedelta] = None
    main: t.Optional[datetime.timedelta] = None
    post_command: t.Optional[datetime.timedelta] = None
    stage_out: t.Optional[datetime.timedelta] = None

    @classmethod
    def from_dict(cls, input_dict: t.Dict[str, t.Union[str]]) -> "ConsumedTime":
        return cls(
            total=_parse_none_or_timedelta(input_dict["total"]),
            queued=_parse_none_or_timedelta(input_dict["queued"]),
            stage_in=_parse_none_or_timedelta(input_dict["stage-in"]),
            pre_command=_parse_none_or_timedelta(input_dict["preCommand"]),
            main=_parse_none_or_timedelta(input_dict["main"]),
            post_command=_parse_none_or_timedelta(input_dict["postCommand"]),
            stage_out=_parse_none_or_timedelta(input_dict["stage-out"]),
        )

    def to_dict(self) -> t.Dict[str, t.Optional[str]]:
        return {
            "total": _format_timedelta(self.total),
            "queued": _format_timedelta(self.queued),
            "stage-in": _format_timedelta(self.stage_in),
            "preCommand": _format_timedelta(self.pre_command),
            "main": _format_timedelta(self.main),
            "postCommand": _format_timedelta(self.post_command),
            "stage-out": _format_timedelta(self.stage_out),
        }


def _parse_none_or_timedelta(
    string: str,
) -> t.Optional[datetime.timedelta]:
    if string == "N/A":
        return None
    return datetime.timedelta(seconds=int(string))


def _format_timedelta(
    td: t.Optional[datetime.timedelta],
) -> t.Optional[str]:
    return None if td is None else str(td)


@dataclasses.dataclass
class Properties:
    """UNICORE Job properties."""

    status: Status
    logs: t.List[str]
    owner: str
    site_name: str
    consumed_time: ConsumedTime
    current_time: datetime.datetime
    submission_time: datetime.datetime
    termination_time: datetime.datetime
    status_message: str
    tags: t.List[str]
    resource_status: str
    name: str
    queue: str
    submission_preferences: dict
    resource_status_message: str
    acl: t.List[str]
    batch_system_id: str
    exit_code: t.Optional[str] = None

    @classmethod
    def from_dict(cls, input_dict: t.Dict) -> "Properties":
        return cls(
            status=Status[input_dict["status"]],
            logs=input_dict["log"],
            owner=input_dict["owner"],
            site_name=input_dict["siteName"],
            consumed_time=ConsumedTime.from_dict(input_dict["consumedTime"]),
            current_time=_parse_datetime(input_dict["submissionTime"]),
            submission_time=_parse_datetime(input_dict["submissionTime"]),
            termination_time=_parse_datetime(input_dict["terminationTime"]),
            status_message=input_dict["statusMessage"],
            tags=input_dict["tags"],
            resource_status=input_dict["resourceStatus"],
            name=input_dict["name"],
            queue=input_dict["queue"],
            submission_preferences=input_dict["submissionPreferences"],
            resource_status_message=input_dict["resourceStatusMessage"],
            acl=input_dict["acl"],
            batch_system_id=input_dict["batchSystemID"],
            exit_code=input_dict.get("exitCode"),
        )

    def to_dict(self):
        return {
            "Status": self.status.value,
            "Logs": self.logs,
            "Owner": self.owner,
            "SiteName": self.site_name,
            "ConsumedTime": self.consumed_time.to_dict(),
            "CurrentTime": self.current_time.isoformat(),
            "SubmissionTime": self.submission_time.isoformat(),
            "TerminationTime": self.termination_time.isoformat(),
            "StatusMessage": self.status_message,
            "Tags": self.tags,
            "ResourceStatus": self.resource_status,
            "Name": self.name,
            "Queue": self.queue,
            "SubmissionPreferences": self.submission_preferences,
            "ResourceStatusMessage": self.resource_status_message,
            "ACL": self.acl,
            "BatchSystemID": self.batch_system_id,
            "ExitCode": self.exit_code,
        }


def _parse_datetime(date: str) -> datetime.datetime:
    return datetime.datetime.strptime(date, UNICORE_TIMESTAMP_FORMAT)
