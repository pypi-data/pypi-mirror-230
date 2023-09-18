import datetime
import enum
import json
from typing import Any, Optional

import pydantic

from ...serde import pydantic_jsonable_dict
from .action_container_resources import (
    ComputeRequirements,
    ContainerParameters,
)


class InvocationDataSourceType(enum.Enum):
    """Source of data for an Action's InputBinding"""

    Dataset = "Dataset"


class InvocationDataSource(pydantic.BaseModel):
    data_source_type: InvocationDataSourceType
    # The "type" determines the meaning of "id":
    #   - if type is "Dataset," id is a dataset_id
    data_source_id: str


class ActionProvenance(pydantic.BaseModel):
    name: str
    org_id: str
    # 2023-09-11 (GM): Optional for backwards compatibility; new invocations will always have a digest
    digest: Optional[str] = None


class InvocationSource(enum.Enum):
    Trigger = "Trigger"
    Manual = "Manual"


class SourceProvenance(pydantic.BaseModel):
    source_type: InvocationSource
    # The “type” determines the meaning of “id:”
    #   - if type is “Trigger,” id is a TriggerId;
    #   - if type is “Manual,” id is a UserId.
    source_id: str


class InvocationProvenance(pydantic.BaseModel):
    action: ActionProvenance
    """The Action that was invoked."""

    source: SourceProvenance
    """The source of the invocation."""


class InvocationStatus(enum.Enum):
    Queued = 0
    Scheduled = 1
    Downloading = 2
    Processing = 3
    Uploading = 4
    Completed = 5
    # Failure status' exist outside linear progression of invocation status
    Failed = 998
    Deadly = 999

    def __str__(self) -> str:
        return self.name

    def can_transition_to(self, other: "InvocationStatus") -> bool:
        if self == other:
            return True

        if self in {InvocationStatus.Completed, InvocationStatus.Deadly}:
            return False

        if self is InvocationStatus.Failed:
            if other in {InvocationStatus.Queued, InvocationStatus.Deadly}:
                return True
            return False

        if other is InvocationStatus.Failed:
            return True

        if other is InvocationStatus.Deadly:
            return self in {InvocationStatus.Queued, InvocationStatus.Failed}

        return other.value - self.value == 1

    def is_running(self) -> bool:
        return self in {
            InvocationStatus.Downloading,
            InvocationStatus.Processing,
            InvocationStatus.Uploading,
        }

    def is_terminal(self) -> bool:
        return self in {
            InvocationStatus.Completed,
            InvocationStatus.Failed,
            InvocationStatus.Deadly,
        }

    def next(self) -> Optional["InvocationStatus"]:
        if self.is_terminal():
            return None
        return InvocationStatus(self.value + 1)


class InvocationStatusRecord(pydantic.BaseModel):
    status: InvocationStatus
    detail: Optional[str] = None
    timestamp: datetime.datetime  # Persisted as ISO 8601 string in UTC

    def to_presentable_dict(self) -> dict[str, Optional[str]]:
        return {
            "status": str(self.status),
            "timestamp": self.timestamp.isoformat(),
            "detail": self.detail,
        }


class LogsLocation(pydantic.BaseModel):
    bucket: str
    prefix: str


class InvocationRecord(pydantic.BaseModel):
    # When adding or removing fields, make sure to update __str__
    created: datetime.datetime  # Persisted as ISO 8601 string in UTC
    data_source: InvocationDataSource
    input_data: list[str]
    invocation_id: str  # Sort key
    idempotency_id: Optional[str] = None
    compute_requirements: ComputeRequirements
    container_parameters: ContainerParameters
    logs: Optional[LogsLocation] = None
    org_id: str  # Partition key
    parameter_values: dict[str, Any] = pydantic.Field(default_factory=dict)
    provenance: InvocationProvenance
    status: list[InvocationStatusRecord] = pydantic.Field(default_factory=list)

    def __str__(self) -> str:
        return json.dumps(
            {
                "created": self.created.isoformat(),
                "data_source": pydantic_jsonable_dict(self.data_source),
                "input_data": self.input_data,
                "invocation_id": self.invocation_id,
                "idempotency_id": self.idempotency_id,
                "logs": self.logs.dict() if self.logs else None,
                "compute_requirements": pydantic_jsonable_dict(
                    self.compute_requirements
                ),
                "container_parameters": pydantic_jsonable_dict(
                    self.container_parameters
                ),
                "org_id": self.org_id,
                "parameter_values": self.parameter_values,
                "provenance": pydantic_jsonable_dict(self.provenance),
                "status": [
                    status_record.to_presentable_dict() for status_record in self.status
                ],
            },
            indent=2,
        )


class LogRecord(pydantic.BaseModel):
    log: str
    timestamp: datetime.datetime
