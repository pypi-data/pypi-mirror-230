import abc
import enum
import pathlib
from typing import Optional, Protocol

from ...http import PaginatedList
from ...query import QuerySpecification
from .progress import (
    NoopProgressMonitorFactory,
    ProgressMonitorFactory,
)
from .record import FileRecord


class FileTag(enum.Enum):
    DatasetId = "dataset_id"
    OrgId = "org_id"
    # Path to file relative to common prefix
    CommonPrefix = "common_prefix"
    UploadId = "upload_id"


class S3Credentials(Protocol):
    access_key_id: str
    secret_access_key: str
    session_token: str


class FileDelegate(abc.ABC):
    @abc.abstractmethod
    def delete_file(self, record: FileRecord) -> None:
        raise NotImplementedError("delete_file")

    @abc.abstractmethod
    def download_file(
        self,
        record: FileRecord,
        local_path: pathlib.Path,
        credentials: S3Credentials,
        progress_monitor_factory: ProgressMonitorFactory = NoopProgressMonitorFactory(),
    ) -> None:
        raise NotImplementedError("download_file")

    @abc.abstractmethod
    def get_record_by_primary_key(
        self, file_id: str, org_id: Optional[str] = None
    ) -> FileRecord:
        raise NotImplementedError("get_record_by_primary_key")

    @abc.abstractmethod
    def get_signed_url(self, record: FileRecord) -> str:
        raise NotImplementedError("get_signed_url")

    @abc.abstractmethod
    def query_files(
        self,
        query: QuerySpecification,
        org_id: Optional[str] = None,
    ) -> PaginatedList[FileRecord]:
        raise NotImplementedError("query_files")

    @abc.abstractmethod
    def upload_file(
        self,
        local_path: pathlib.Path,
        bucket: str,
        key: str,
        credentials: S3Credentials,
        tags: Optional[dict[FileTag, str]] = None,
        progress_monitor_factory: ProgressMonitorFactory = NoopProgressMonitorFactory(),
    ) -> None:
        raise NotImplementedError("upload_file")
