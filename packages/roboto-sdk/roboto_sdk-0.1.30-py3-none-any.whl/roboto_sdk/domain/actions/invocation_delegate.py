import abc
from typing import Any, Optional

from ...http import PaginatedList, StreamedList
from ...query import QuerySpecification
from .action_container_resources import (
    ComputeRequirements,
    ContainerParameters,
)
from .action_record import ActionRecord
from .invocation_record import (
    InvocationDataSourceType,
    InvocationRecord,
    InvocationSource,
    InvocationStatus,
    LogRecord,
    LogsLocation,
)


class InvocationDelegate(abc.ABC):
    @abc.abstractmethod
    def create_invocation(
        self,
        action_record: ActionRecord,
        parameter_values: dict[str, Any],
        input_data: list[str],
        compute_requirements: ComputeRequirements,
        container_parameters: ContainerParameters,
        data_source_id: str,
        data_source_type: InvocationDataSourceType,
        invocation_source: InvocationSource,
        invocation_source_id: Optional[str] = None,
        idempotency_id: Optional[str] = None,
        org_id: Optional[str] = None,
    ) -> InvocationRecord:
        raise NotImplementedError("create_invocation")

    @abc.abstractmethod
    def get_by_id(
        self, invocation_id: str, org_id: Optional[str] = None
    ) -> InvocationRecord:
        raise NotImplementedError("get_by_id")

    @abc.abstractmethod
    def get_logs(
        self,
        invocation_id: str,
        page_token: Optional[str] = None,
        org_id: Optional[str] = None,
    ) -> PaginatedList[LogRecord]:
        raise NotImplementedError("get_logs")

    @abc.abstractmethod
    def stream_logs(
        self,
        invocation_id: str,
        last_read: Optional[str] = None,
        org_id: Optional[str] = None,
    ) -> StreamedList[LogRecord]:
        raise NotImplementedError("stream_logs")

    @abc.abstractmethod
    def set_logs_location(
        self,
        record: InvocationRecord,
        logs: LogsLocation,
    ) -> InvocationRecord:
        raise NotImplementedError("set_logs_location")

    @abc.abstractmethod
    def update_invocation_status(
        self,
        record: InvocationRecord,
        status: InvocationStatus,
        detail: Optional[str] = None,
    ) -> InvocationRecord:
        raise NotImplementedError("update_invocation_status")

    @abc.abstractmethod
    def query_invocations(
        self,
        query: QuerySpecification,
        org_id: Optional[str] = None,
    ) -> PaginatedList[InvocationRecord]:
        raise NotImplementedError("query_invocations")
