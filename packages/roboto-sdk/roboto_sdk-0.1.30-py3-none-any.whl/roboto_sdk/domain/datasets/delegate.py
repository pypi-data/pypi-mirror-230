import abc
import datetime
from typing import Any, Optional

import pydantic

from ...auth import Permissions
from ...http import PaginatedList
from ...query import QuerySpecification
from ...serde import pydantic_jsonable_dict
from ...time import utcnow
from ...updates import (
    MetadataChangeset,
    UpdateCondition,
)
from ..files import FileRecord
from .record import (
    Administrator,
    DatasetRecord,
    StorageLocation,
)


class Credentials(pydantic.BaseModel):
    access_key_id: str
    bucket: str
    expiration: datetime.datetime
    secret_access_key: str
    session_token: str
    required_prefix: str
    upload_id: Optional[str] = None

    def is_expired(self) -> bool:
        return utcnow() >= self.expiration

    def to_dict(self) -> dict[str, Any]:
        return pydantic_jsonable_dict(self, exclude_none=True)


class DatasetDelegate(abc.ABC):
    @abc.abstractmethod
    def complete_upload(
        self, dataset_id: str, upload_id: str, org_id: Optional[str] = None
    ) -> None:
        raise NotImplementedError("complete_upload")

    @abc.abstractmethod
    def create_dataset(
        self,
        administrator: Administrator = Administrator.Roboto,
        metadata: Optional[dict[str, Any]] = None,
        storage_location: StorageLocation = StorageLocation.S3,
        tags: Optional[list[str]] = None,
        org_id: Optional[str] = None,
        created_by: Optional[str] = None,
        description: Optional[str] = None,
    ) -> DatasetRecord:
        raise NotImplementedError("create_dataset")

    @abc.abstractmethod
    def delete_dataset(self, record: DatasetRecord) -> None:
        raise NotImplementedError("delete_dataset")

    @abc.abstractmethod
    def get_dataset_by_primary_key(
        self,
        dataset_id: str,
        org_id: Optional[str] = None,
    ) -> DatasetRecord:
        raise NotImplementedError("get_dataset_by_primary_key")

    @abc.abstractmethod
    def get_temporary_credentials(
        self,
        record: DatasetRecord,
        permissions: Permissions,
        caller: Optional[str] = None,
        transaction_id: Optional[str] = None,
    ) -> Credentials:
        raise NotImplementedError("get_temporary_credentials")

    @abc.abstractmethod
    def list_files(
        self,
        dataset_id: str,
        org_id: Optional[str] = None,
        page_token: Optional[str] = None,
    ) -> PaginatedList[FileRecord]:
        raise NotImplementedError("list_files")

    @abc.abstractmethod
    def query_datasets(
        self,
        query: QuerySpecification,
        org_id: Optional[str] = None,
    ) -> PaginatedList[DatasetRecord]:
        raise NotImplementedError("query_datasets")

    @abc.abstractmethod
    def update(
        self,
        record: DatasetRecord,
        metadata_changeset: Optional[MetadataChangeset] = None,
        conditions: Optional[list[UpdateCondition]] = None,
        description: Optional[str] = None,
        updated_by: Optional[str] = None,
    ) -> DatasetRecord:
        raise NotImplementedError("update")
