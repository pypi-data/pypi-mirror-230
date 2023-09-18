#  Copyright (c) 2023 Roboto Technologies, Inc.
import typing

import pydantic

from .record import (
    OrgRoleName,
    OrgStatus,
    OrgType,
)


class CreateOrgRequest(pydantic.BaseModel):
    org_type: OrgType
    name: str
    bind_email_domain: bool = False


class OrgRecordUpdates(pydantic.BaseModel):
    name: typing.Optional[str] = None
    org_type: typing.Optional[OrgType] = None
    status: typing.Optional[OrgStatus] = None


class UpdateOrgRequest(pydantic.BaseModel):
    updates: OrgRecordUpdates


class BindEmailDomainRequest(pydantic.BaseModel):
    email_domain: str


class InviteUserRequest(pydantic.BaseModel):
    invited_user_id: str


class ModifyRoleForUserRequest(pydantic.BaseModel):
    user_id: str
    role_name: OrgRoleName


class RemoveUserFromOrgRequest(pydantic.BaseModel):
    user_id: str
