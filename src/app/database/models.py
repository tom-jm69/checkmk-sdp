#!/usr/bin/env python3
# Copyright (C) 2025-present Tom Müller - License: GNU General Public License v3
# This file is part of the Checkmk-sdp API client. It is subject to the terms and
# conditions defined in the file LICENSE or at <https://www.gnu.org/licenses/>.

from typing import Any, Mapping, Optional

from pydantic import BaseModel


class CombinedRequest(BaseModel):
    servicedesk_request_id: Optional[int] = None
    servicedesk_request_state: Optional[str] = None
    checkmk_problem_id: Optional[int] = None
    checkmk_state: Optional[str] = None
    checkmk_type: Optional[str] = None

    @classmethod
    def from_sqlite_row(cls, row: Mapping[str, Any]) -> "CombinedRequest":
        """
        Create a Request instance from a sqlite3.Row or asqlite row (dict-like).
        """
        return cls(
            servicedesk_request_id=row["servicedesk_request_id"],
            servicedesk_request_state=row["request_state"],
            checkmk_problem_id=row["problem_id"],
            checkmk_state=row["checkmk_state"],
            checkmk_type=row["checkmk_type"],
        )


class CheckmkInfo(BaseModel):
    id: Optional[int] = None
    host_name: Optional[str] = None
    service_check_command: Optional[str] = None
    service_description: Optional[str] = None
    acknowledged: Optional[int] = None
    state: Optional[str] = None
    type: Optional[str] = None

    @classmethod
    def from_sqlite_row(cls, row: Mapping[str, Any]) -> "CheckmkInfo":
        """
        Create a Request instance from a sqlite3.Row or asqlite row (dict-like).
        """
        return cls(
            id=row["id"],
            host_name=row["host_name"],
            service_check_command=row["service_check_command"],
            service_description=row["service_description"],
            acknowledged=row["acknowledged"],
            state=row["state"],
            type=row["type"],
        )
