#!/usr/bin/env python3
# Copyright (C) 2025-present Tom Müller - License: GNU General Public License v3
# This file is part of the Checkmk-sdp API client. It is subject to the terms and
# conditions defined in the file LICENSE or at <https://www.gnu.org/licenses/>.

from datetime import datetime
from typing import Any, Dict, List, Optional

from dateutil import parser
from dateutil.tz import gettz
from pydantic import BaseModel, Field, HttpUrl, field_validator

tzinfos = {
    "CEST": gettz("Europe/Berlin"),
    "CET": gettz("Europe/Berlin"),  # for winter time
}
# https://github.com/Checkmk/checkmk/blob/master/cmk/utils/livestatus_helpers/tables/services.py


class Comment(BaseModel):
    id: Optional[int] = None
    author: Optional[str] = None
    comment: Optional[str] = None
    entry_type: Optional[int] = None
    entry_time: Optional[datetime] = None


class ServiceComment(BaseModel):
    comment: Optional[str] = None
    persistent: Optional[bool] = True
    host_name: Optional[str] = None
    service_description: Optional[str] = None
    comment_type: Optional[str] = "service"


class HostComment(BaseModel):
    comment: Optional[str] = None
    persistent: Optional[bool] = True
    host_name: Optional[str] = None
    comment_type: Optional[str] = "host"


class ServiceAcknowledgement(BaseModel):
    comment: Optional[str] = None
    service_description: Optional[str] = None
    host_name: Optional[str] = None
    sticky: Optional[bool] = True
    persistent: Optional[bool] = False
    notify: Optional[bool] = True
    acknowledge_type: Optional[str] = "service"


class HostAcknowledgement(BaseModel):
    comment: Optional[str] = None
    host_name: Optional[str] = None
    sticky: Optional[bool] = True
    persistent: Optional[bool] = False
    notify: Optional[bool] = True
    acknowledge_type: Optional[str] = "host"


class ServiceNotification(BaseModel):
    checkmk_base_url: Optional[str] = None
    service_problem_id: Optional[str] = Field(None, alias="NOTIFY_SERVICEPROBLEMID")
    service_name: Optional[str] = Field(None, alias="NOTIFY_SERVICECHECKCOMMAND")
    service_desc: Optional[str] = Field(None, alias="NOTIFY_SERVICEDESC")
    service_state: Optional[str] = Field(None, alias="NOTIFY_SERVICESTATE")
    service_output_long: Optional[str] = Field(None, alias="NOTIFY_LONGSERVICEOUTPUT")
    service_output_short: Optional[str] = Field(None, alias="NOTIFY_SERVICEOUTPUT")
    notification_datetime_long: Optional[datetime] = Field(
        None, alias="NOTIFY_LONGDATETIME"
    )
    notification_type: Optional[str] = Field(None, alias="NOTIFY_NOTIFICATIONTYPE")
    service_check_command: Optional[str] = Field(
        None, alias="NOTIFY_SERVICECHECKCOMMAND"
    )
    host_alias: Optional[str] = Field(None, alias="NOTIFY_HOSTALIAS")
    host_ipv4: Optional[str] = Field(None, alias="NOTIFY_HOST_ADDRESS_4")
    host_name: Optional[str] = Field(None, alias="NOTIFY_HOSTNAME")
    host_state_id: Optional[int] = Field(None, alias="NOTIFY_HOSTSTATEID")
    host_state: Optional[str] = Field(None, alias="NOTIFY_HOSTSTATE")
    host_state_short: Optional[str] = Field(None, alias="NOTIFY_HOSTSHORTSTATE")
    host_output: Optional[str] = Field(None, alias="NOTIFY_HOSTOUTPUT")
    host_performance_data: Optional[str] = Field(None, alias="NOTIFY_HOSTPERFDATA")
    host_check_command: Optional[str] = Field(None, alias="NOTIFY_HOSTCHECKCOMMAND")
    service_last_state_change: Optional[datetime] = Field(
        None, alias="NOTIFY_LASTSERVICESTATECHANGE"
    )
    host_url: Optional[str] = Field(None, alias="NOTIFY_HOSTURL")
    service_url: Optional[str] = Field(None, alias="NOTIFY_HOSTURL")
    contacts: Optional[str] = Field(None, alias="NOTIFY_CONTACTS")

    @field_validator("notification_datetime_long", mode="before")
    def parse_long_datetime(cls, value: str) -> datetime:
        return parser.parse(value, tzinfos=tzinfos)

    class Config:
        populate_by_name = True


class HostNotification(BaseModel):
    checkmk_base_url: Optional[str] = None
    site_name: Optional[str] = Field(None, alias="OMD_SITE")
    user_name: Optional[str] = Field(None, alias="USER")
    host_alias: Optional[str] = Field(None, alias="NOTIFY_HOSTALIAS")
    host_address_ipv4: Optional[str] = Field(None, alias="NOTIFY_HOSTADDRESS")
    host_name: Optional[str] = Field(None, alias="NOTIFY_HOSTNAME")
    host_state_id: Optional[int] = Field(None, alias="NOTIFY_HOSTSTATEID")
    host_state: Optional[str] = Field(None, alias="NOTIFY_HOSTSTATE")
    host_state_short: Optional[str] = Field(None, alias="NOTIFY_HOSTSHORTSTATE")
    host_output: Optional[str] = Field(None, alias="NOTIFY_HOSTOUTPUT")
    host_performance_data: Optional[str] = Field(None, alias="NOTIFY_HOSTPERFDATA")
    host_check_command: Optional[str] = Field(None, alias="NOTIFY_HOSTCHECKCOMMAND")
    host_tags: Optional[str] = Field(None, alias="NOTIFY_HOSTTAGS")
    host_group_names: Optional[str] = Field(None, alias="NOTIFY_HOSTGROUPNAMES")
    host_notification_number: Optional[int] = Field(
        None, alias="NOTIFY_HOSTNOTIFICATIONNUMBER"
    )
    host_downtime: Optional[str] = Field(None, alias="NOTIFY_HOSTDOWNTIME")
    host_attempt: Optional[str] = Field(None, alias="NOTIFY_HOSTATTEMPT")
    host_ack_author: Optional[str] = Field(None, alias="NOTIFY_HOSTACKAUTHOR")
    host_ack_comment: Optional[str] = Field(None, alias="NOTIFY_HOSTACKCOMMENT")
    host_last_state: Optional[str] = Field(None, alias="NOTIFY_LASTHOSTSTATE")
    host_last_state_id: Optional[str] = Field(None, alias="NOTIFY_LASTHOSTSTATEID")
    host_last_problem_id: Optional[str] = Field(None, alias="NOTIFY_LASTHOSTPROBLEMID")
    host_last_up: Optional[datetime] = Field(None, alias="NOTIFY_LASTHOSTUP")
    host_last_state_change: Optional[datetime] = Field(
        None, alias="NOTIFY_LASTHOSTSTATECHANGE"
    )
    host_last_state_change_rel: Optional[str] = Field(
        None, alias="NOTIFY_LASTHOSTSTATECHANGE_REL"
    )
    host_last_up_rel: Optional[str] = Field(None, alias="NOTIFY_LASTHOSTUP_REL")
    host_previous_hard_state: Optional[str] = Field(
        None, alias="NOTIFY_PREVIOUSHOSTHARDSTATE"
    )
    host_previous_hard_state_short: Optional[str] = Field(
        None, alias="NOTIFY_PREVIOUSHOSTHARDSHORTSTATE"
    )
    host_ipv4: Optional[str] = Field(None, alias="NOTIFY_HOST_ADDRESS_4")
    host_address_family: Optional[int] = Field(None, alias="NOTIFY_HOST_ADDRESS_FAMILY")
    host_for_url: Optional[str] = Field(None, alias="NOTIFY_HOSTFORURL")
    host_url: Optional[str] = Field(None, alias="NOTIFY_HOSTURL")
    host_long_output: Optional[str] = Field(None, alias="NOTIFY_LONGHOSTOUTPUT")
    host_problem_id: Optional[str] = Field(None, alias="NOTIFY_HOSTPROBLEMID")

    notification_comment: Optional[str] = Field(
        None, alias="NOTIFY_NOTIFICATIONCOMMENT"
    )
    notification_author_name: Optional[str] = Field(
        None, alias="NOTIFY_NOTIFICATIONAUTHORNAME"
    )
    notification_author: Optional[str] = Field(None, alias="NOTIFY_NOTIFICATIONAUTHOR")
    notification_author_alias: Optional[str] = Field(
        None, alias="NOTIFY_NOTIFICATIONAUTHORALIAS"
    )

    notification_datetime_long: Optional[datetime] = Field(
        None, alias="NOTIFY_LONGDATETIME"
    )
    notification_datetime_short: Optional[datetime] = Field(
        None, alias="NOTIFY_SHORTDATETIME"
    )
    notification_date: Optional[datetime] = Field(None, alias="NOTIFY_DATE")

    monitoring_host: Optional[str] = Field(None, alias="NOTIFY_MONITORING_HOST")
    omd_site: Optional[str] = Field(None, alias="NOTIFY_OMD_SITE")
    omd_root: Optional[str] = Field(None, alias="NOTIFY_OMD_ROOT")
    log_dir: Optional[str] = Field(None, alias="NOTIFY_LOGDIR")
    micro_time: Optional[int] = Field(None, alias="NOTIFY_MICROTIME")
    contacts: Optional[str] = Field(None, alias="NOTIFY_CONTACTS")

    @field_validator("notification_datetime_long", mode="before")
    def parse_long_datetime(cls, value: str) -> datetime:
        return parser.parse(value, tzinfos=tzinfos)

    @field_validator("host_last_state_change", mode="before")
    @classmethod
    def parse_host_last_state_change(cls, value: str) -> datetime:
        return datetime.fromtimestamp(int(value))

    @field_validator("notification_datetime_short", mode="before")
    @classmethod
    def parse_short_datetime(cls, value: str) -> datetime:
        return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")

    @field_validator("notification_date", mode="before")
    @classmethod
    def parse_date(cls, value: str) -> datetime:
        return datetime.strptime(value, "%Y-%m-%d")

    class Config:
        populate_by_name = True


class ServiceExtensions(BaseModel):
    description: Optional[str] = None
    host_name: Optional[str] = None
    state: Optional[int] = None
    acknowledged: Optional[int] = None
    acknowledgement_type: Optional[int] = None
    check_command: Optional[str] = None
    check_command_expanded: Optional[str] = None
    check_flapping_recovery_notification: Optional[int] = None
    check_freshness: Optional[int] = None
    check_interval: Optional[float] = None
    check_options: Optional[int] = None
    check_period: Optional[str] = None
    check_type: Optional[int] = None
    checks_enabled: Optional[int] = None
    comments_with_extra_info: Optional[List[Comment]] = None
    contact_groups: Optional[List] = None
    contacts: Optional[List] = None
    current_attempt: Optional[int] = None
    current_notification_number: Optional[int] = None
    custom_variable_names: Optional[List] = None
    custom_variable_values: Optional[List] = None
    custom_variables: Optional[Dict] = None
    display_name: Optional[str] = None
    downtimes: Optional[List] = None
    downtimes_with_extra_info: Optional[List] = None
    downtimes_with_info: Optional[List] = None
    event_handler: Optional[str] = None
    event_handler_enabled: Optional[int] = None
    execution_time: Optional[float] = None
    first_notification_delay: Optional[float] = None
    flap_detection_enabled: Optional[int] = None
    flappiness: Optional[float] = None
    groups: Optional[List] = None
    hard_state: Optional[int] = None
    has_been_checked: Optional[int] = None
    high_flap_threshold: Optional[float] = None

    # Extended fields
    icon_image: Optional[str] = None
    icon_image_alt: Optional[str] = None
    icon_image_expanded: Optional[str] = None
    in_check_period: Optional[int] = None
    in_notification_period: Optional[int] = None
    in_service_period: Optional[int] = None
    initial_state: Optional[int] = None
    is_executing: Optional[int] = None
    is_flapping: Optional[int] = None
    label_names: Optional[List[str]] = None
    label_source_names: Optional[List[str]] = None
    label_source_values: Optional[List[str]] = None
    label_sources: Optional[Dict] = None
    label_values: Optional[List[str]] = None
    labels: Optional[Dict[str, str]] = None
    last_check: Optional[datetime] = None
    last_hard_state: Optional[int] = None
    last_hard_state_change: Optional[int] = None
    last_notification: Optional[int] = None
    last_state: Optional[int] = None
    last_state_change: Optional[int] = None
    last_time_down: Optional[int] = None
    last_time_unreachable: Optional[int] = None
    last_time_up: Optional[int] = None
    latency: Optional[float] = None
    long_plugin_output: Optional[str] = None
    low_flap_threshold: Optional[float] = None
    max_check_attempts: Optional[int] = None
    metrics: Optional[List] = None
    mk_inventory: Optional[bytes] = None
    mk_inventory_gz: Optional[bytes] = None
    mk_inventory_last: Optional[int] = None
    mk_logwatch_files: Optional[List[str]] = None
    modified_attributes: Optional[int] = None
    modified_attributes_list: Optional[List[str]] = None
    next_check: Optional[int] = None
    next_notification: Optional[int] = None
    no_more_notifications: Optional[int] = None
    notes: Optional[str] = None
    notes_expanded: Optional[str] = None
    notes_url: Optional[str] = None
    notes_url_expanded: Optional[str] = None
    notification_interval: Optional[float] = None
    notification_period: Optional[str] = None
    notification_postponement_reason: Optional[str] = None
    notifications_enabled: Optional[int] = None
    num_services: Optional[int] = None
    num_services_crit: Optional[int] = None
    num_services_handled_problems: Optional[int] = None
    num_services_hard_crit: Optional[int] = None
    num_services_hard_ok: Optional[int] = None
    num_services_hard_unknown: Optional[int] = None
    num_services_hard_warn: Optional[int] = None
    num_services_ok: Optional[int] = None
    num_services_pending: Optional[int] = None
    num_services_unhandled_problems: Optional[int] = None
    num_services_unknown: Optional[int] = None
    num_services_warn: Optional[int] = None
    obsess_over_host: Optional[int] = None
    parents: Optional[List[str]] = None
    pending_flex_downtime: Optional[int] = None
    percent_state_change: Optional[float] = None
    perf_data: Optional[str] = None
    performance_data: Optional[Dict[str, float]] = None
    plugin_output: Optional[str] = None
    pnpgraph_present: Optional[int] = None
    previous_hard_state: Optional[int] = None
    process_performance_data: Optional[int] = None
    retry_interval: Optional[float] = None
    scheduled_downtime_depth: Optional[int] = None
    service_period: Optional[str] = None
    services: Optional[List] = None
    services_with_fullstate: Optional[List] = None
    services_with_info: Optional[List] = None
    services_with_state: Optional[List] = None
    smartping_timeout: Optional[int] = None
    staleness: Optional[float] = None
    state_type: Optional[int] = None
    statusmap_image: Optional[str] = None
    structured_status: Optional[bytes] = None
    tag_names: Optional[List[str]] = None
    tag_values: Optional[List[str]] = None
    tags: Optional[Dict[str, str]] = None
    total_services: Optional[int] = None
    worst_service_hard_state: Optional[int] = None
    worst_service_state: Optional[int] = None

    @field_validator("long_plugin_output", mode="before")
    @classmethod
    def replace_long_plugin_output(cls, value: str) -> str:
        return value.replace(r"\\n", "")

    @property
    def state_name(self) -> str:
        state_map = {0: "OK", 1: "WARNING", 2: "CRITICAL", 3: "UNKNOWN"}
        return state_map.get(self.state, "UNDEFINED")

    @field_validator("comments_with_extra_info", mode="before")
    @classmethod
    def parse_comment_lists(cls, v):
        if isinstance(v, list) and all(isinstance(item, list) for item in v):
            return [
                Comment(
                    id=item[0],
                    author=item[1],
                    comment=item[2],
                    entry_type=item[3],
                    entry_time=datetime.fromtimestamp(item[4]) if item[4] else None,
                )
                for item in v
            ]
        return v


class MetaData(BaseModel):
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    created_by: Optional[str]


class Attributes(BaseModel):
    alias: Optional[str] = None
    meta_data: Optional[MetaData]
    labels: Optional[Dict[str, str]] = None
    tag_address_family: Optional[str] = None


class HostExtensions(BaseModel):
    name: Optional[str] = None
    state: Optional[int] = None
    last_check: Optional[int] = None
    acknowledged: Optional[int] = None
    acknowledgement_type: Optional[int] = None


class HostModel(BaseModel):
    domainType: str
    id: str
    title: str
    members: Optional[Dict[str, Any]] = None
    extensions: Optional[HostExtensions] = None


# Services
class Link(BaseModel):
    domainType: Optional[str] = None
    href: Optional[HttpUrl] = None
    method: Optional[str] = None
    rel: Optional[str] = None
    title: Optional[str] = None
    type: Optional[str] = None


class ServiceModel(BaseModel):
    domainType: Optional[str] = None
    extensions: Optional[ServiceExtensions] = None
    id: Optional[str] = None
    links: Optional[List[Link]] = None
    members: Optional[Dict] = None
    title: Optional[str] = None
    updated_at: Optional[datetime] = datetime.now()


class ColumnsRequest(BaseModel):
    columns: Optional[List[str]] = None
