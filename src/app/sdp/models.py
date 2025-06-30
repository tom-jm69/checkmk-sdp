#!/usr/bin/env python3
# Copyright (C) 2025-present Tom Müller - License: GNU General Public License v3
# This file is part of the Checkmk-sdp API client. It is subject to the terms and
# conditions defined in the file LICENSE or at <https://www.gnu.org/licenses/>.

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator

import src.conf as conf

from .enums import PriorityEnum


class Attachment(BaseModel):
    authentication_id: Optional[str] = None
    content_type: Optional[str] = None
    content_url: Optional[str] = None
    id: Optional[int] = None
    module: Optional[str] = None
    name: Optional[str] = None
    size: Optional[Dict[str, Any]] = None


class SubCategory(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None


class Category(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None


class Mode(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None


class ServiceCategory(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None


class TimeValue(BaseModel):
    value: Optional[int] = None
    display_value: Optional[str] = None


class TimeValueSDP(BaseModel):
    value: Optional[int] = None


class User(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None


class Technician(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None


class Resolution(BaseModel):
    content: Optional[str] = None


class Status(BaseModel):
    name: Optional[str] = None


class RequestType(BaseModel):
    name: Optional[str] = None
    id: Optional[int] = None


class PickField(BaseModel):
    name: Optional[str] = None
    id: Optional[int] = None


class Template(BaseModel):
    name: Optional[str] = None
    id: Optional[int] = None


class ApprovalConfigurations(BaseModel):
    any_one_can_approve: bool
    all_should_approve: bool


class TaskConfigurations(BaseModel):
    create_after_approval: bool
    trigger_after_creation: bool
    can_requester_view_tasks: bool
    trigger_after_approval: bool


class Filter(BaseModel):
    name: Optional[str] = "All_incidents"


class ServiceTemplateFields(BaseModel):
    servicename: Optional[str] = Field(None, alias=conf.SDP_SERVICE_NAME_API_FIELD)
    servicestatus: Optional[PickField] = Field(
        None, alias=conf.SDP_SERVICE_STATUS_API_FIELD
    )
    serviceoutput: Optional[str] = Field(None, alias=conf.SDP_SERVICE_OUTPUT_API_FIELD)
    serviceoutputlong: Optional[str] = Field(
        None, alias=conf.SDP_SERVICE_OUTPUT_LONG_API_FIELD
    )
    servicedescription: Optional[str] = Field(
        None, alias=conf.SDP_SERVICE_DESCRIPTION_API_FIELD
    )
    servicelaststatechange: Optional[TimeValueSDP] = Field(
        None, alias=conf.SDP_SERVICE_LAST_STATE_CHANGE_API_FIELD
    )
    servicecheckcommand: Optional[str] = Field(
        None, alias=conf.SDP_SERVICE_CHECK_COMMAND_API_FIELD
    )
    serviceurl: Optional[str] = Field(None, alias=conf.SDP_SERVICE_URL_API_FIELD)
    hostname: Optional[str] = Field(None, alias=conf.SDP_HOST_NAME_API_FIELD)
    hostalias: Optional[str] = Field(None, alias=conf.SDP_HOST_ALIAS_API_FIELD)
    hostipv4: Optional[str] = Field(None, alias=conf.SDP_HOST_IPV4_API_FIELD)
    hoststate: Optional[PickField] = Field(None, alias=conf.SDP_HOST_STATE_API_FIELD)
    hosturl: Optional[str] = Field(None, alias=conf.SDP_HOST_URL_API_FIELD)
    contacts: Optional[str] = Field(None, alias=conf.SDP_CONTACTS_API_FIELD)
    alarmdate: Optional[TimeValueSDP] = Field(None, alias=conf.SDP_ALARM_DATE_API_FIELD)

    class Config:
        populate_by_name = True

    @field_validator("serviceurl", mode="before")
    @classmethod
    def parse_service_url(cls, value: str) -> str:
        return f"{conf.CHECKMK_SCHEME}://{conf.CHECKMK_URL}:{conf.CHECKMK_PORT}/{conf.CHECKMK_SITE_NAME}{value}"

    @field_validator("hosturl", mode="before")
    @classmethod
    def parse_host_url(cls, value: str) -> str:
        return f"{conf.CHECKMK_SCHEME}://{conf.CHECKMK_URL}:{conf.CHECKMK_PORT}/{conf.CHECKMK_SITE_NAME}{value}"


class HostTemplateFields(BaseModel):
    hostname: Optional[str] = Field(None, alias=conf.SDP_HOST_NAME_API_FIELD)
    hostalias: Optional[str] = Field(None, alias=conf.SDP_HOST_ALIAS_API_FIELD)
    hostipv4: Optional[str] = Field(None, alias=conf.SDP_HOST_IPV4_API_FIELD)
    hoststate: Optional[PickField] = Field(None, alias=conf.SDP_HOST_STATE_API_FIELD)
    hostcheckcommand: Optional[str] = Field(
        None, alias=conf.SDP_HOST_CHECK_COMMAND_API_FIELD
    )
    hostlaststatechange: Optional[TimeValueSDP] = Field(
        None, alias=conf.SDP_HOST_LAST_STATE_CHANGE_API_FIELD
    )
    hostlaststateup: Optional[TimeValueSDP] = Field(
        None, alias=conf.SDP_HOST_LAST_STATE_UP_API_FIELD
    )
    hosturl: Optional[str] = Field(None, alias=conf.SDP_HOST_URL_API_FIELD)
    contacts: Optional[str] = Field(None, alias=conf.SDP_CONTACTS_API_FIELD)
    alarmdate: Optional[TimeValueSDP] = Field(None, alias=conf.SDP_ALARM_DATE_API_FIELD)
    hostoutput: Optional[str] = Field(None, alias=conf.SDP_HOST_OUTPUT_API_FIELD)

    class Config:
        populate_by_name = True

    @field_validator("hosturl", mode="before")
    @classmethod
    def parse_host_url(cls, value: str) -> str:
        return f"{conf.CHECKMK_SCHEME}://{conf.CHECKMK_URL}:{conf.CHECKMK_PORT}/{conf.CHECKMK_SITE_NAME}{value}"


class RequestPriority(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    color: Optional[str] = None

    @classmethod
    def from_enum(cls, priority_enum: PriorityEnum) -> "RequestPriority":
        return cls(
            id=priority_enum.id,
            name=priority_enum.name,
            color=priority_enum.color,
        )

    def to_enum(self) -> PriorityEnum:
        for p in PriorityEnum:
            if self.id == p.id:
                return p
        raise ValueError(f"No matching PriorityEnum for id={self.id}")

    class Config:
        use_enum_values = (
            False  # preserve enum object if used (not relevant here anymore)
        )


class CreationRequest(BaseModel):
    subject: Optional[str] = None
    description: Optional[str] = None
    requester: Optional[User] = None
    impact_details: Optional[str] = None
    resolution: Optional[Resolution] = None
    status: Optional[Status] = None
    request_type: Optional[RequestType] = None
    template: Optional[Template] = None
    udf_fields: Optional[HostTemplateFields | ServiceTemplateFields] = None
    priority: Optional[RequestPriority] = None


class CreationRequestDataModel(BaseModel):
    request: Optional[CreationRequest] = None


class SearchCriteria(BaseModel):
    field: Optional[str] = None
    values: Optional[Any] = None
    condition: Optional[str] = None
    logical_operator: Optional[str] = None


class ViewRequestsDataModel(BaseModel):
    row_count: Optional[int] = None
    start_index: Optional[int] = None
    sort_field: Optional[str] = None
    sort_order: Optional[str] = None
    get_total_count: Optional[bool] = None
    filter_by: Optional[Filter] = None
    search_criteria: Optional[List[SearchCriteria]] = None


class RequestStatus(BaseModel):
    color: Optional[str] = None
    name: Optional[str] = None
    id: Optional[int] = None


class UpdatedTime(BaseModel):
    display_value: str
    value: str


class ClosureCode(BaseModel):
    name: Optional[str] = None


class ClosureInfo(BaseModel):
    requester_ack_resolution: Optional[bool] = None
    requester_ack_comments: Optional[str] = None
    closure_comments: Optional[str] = None
    closure_code: Optional[ClosureCode] = None


class CloseRequest(BaseModel):
    request: Dict[str, ClosureInfo]


class ResponseStatus(BaseModel):
    status_code: Optional[int] = None
    status: Optional[str] = None


class Message(BaseModel):
    type: str
    message: str
    status_code: str


class ResponseStatusTemplate(BaseModel):
    messages: List[Message]
    id: Optional[str] = None
    status: Optional[str] = None


class CreatedTime(BaseModel):
    display_value: Optional[str] = None
    value: Optional[str] = None


class CreatedBy(BaseModel):
    name: Optional[str] = None
    id: Optional[str] = None


class Position(BaseModel):
    col: Optional[str] = None
    row: Optional[str] = None
    col_size: Optional[str] = None
    row_size: Optional[str] = None


class FieldItem(BaseModel):
    name: Optional[str] = None
    requester_can_edit: Optional[bool] = None
    requester_can_view: Optional[bool] = None
    position: Optional[Position] = None
    mandatory: Optional[bool] = None
    style_properties: Optional[Dict] = None
    height: Optional[str] = None


class Section(BaseModel):
    field_align: Optional[str] = None
    column_count: Optional[str] = None
    name: Optional[str] = None
    collapsed_state: Optional[str] = None
    position: Optional[Position] = None
    fields: Optional[List[FieldItem]] = None
    style_properties: Optional[Dict] = None


class Layout(BaseModel):
    name: Optional[str] = None
    sections: Optional[List[Section]] = None


class Request(BaseModel):
    id: Optional[int] = None
    subject: Optional[str] = None
    priority: Optional[RequestPriority] = None
    short_description: Optional[str] = None
    created_time: Optional[TimeValue] = None
    created_by: Optional[User] = None
    due_by_time: Optional[TimeValue] = None
    is_service_request: Optional[bool] = None
    technician: Optional[Technician] = None
    requester: Optional[User] = None
    is_overdue: Optional[bool] = None
    request_type: Optional[RequestType] = None
    last_updated_time: Optional[TimeValue] = None
    status: Optional[RequestStatus] = None
    template: Optional["RequestTemplate"] = None
    service_category: Optional[ServiceCategory] = None
    category: Optional[Category] = None
    subcategory: Optional[SubCategory] = None
    mode: Optional[Mode] = None
    resolution: Optional[Resolution] = None
    attachments: Optional[List[Attachment]] = None
    closure_info: Optional[ClosureInfo] = None
    is_fcr: Optional[bool] = None
    approval_status: Optional[Dict[str, str]] = None
    is_reopened: Optional[bool] = None
    completed_time: Optional[TimeValue] = None
    resolved_time: Optional[TimeValue] = None
    time_elapsed: Optional[TimeValue] = None
    udf_fields: Optional[Dict[str, Any]] = None
    email_ids_to_notify: Optional[List[str]] = None


class RequestTemplate(BaseModel):
    created_time: Optional[CreatedTime] = None
    request: Optional[Request] = None
    is_service_template: Optional[bool] = None
    service_category: Optional[Dict] = None
    show_to_requester: Optional[bool] = None
    icon: Optional[Dict[str, str]] = None
    description: Optional[str] = None
    created_by: Optional[CreatedBy] = None
    layouts: Optional[List[Layout]] = None
    style_properties: Optional[Dict[str, Optional[Dict]]] = None
    approval_configurations: Optional[ApprovalConfigurations] = None
    is_enabled: Optional[bool] = None
    inactive: Optional[bool] = None
    support_groups: Optional[List] = None
    image_token: Optional[str] = None
    task_templates: Optional[List] = None
    name: Optional[str] = None
    id: Optional[str] = None
    task_configurations: Optional[TaskConfigurations] = None
    user_groups: Optional[List] = None


class ResponseRequestDataModel(BaseModel):
    requests: Optional[List[Request]] = None
    response_status: Optional[List[ResponseStatus]] = None


class IncidentTemplateResponse(BaseModel):
    response_status: Optional[ResponseStatusTemplate] = None
    request_template: Optional[RequestTemplate] = None


class NotificationResponse(BaseModel):
    success: bool
    message: str
    request: Optional[Request] = None
