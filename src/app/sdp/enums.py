#!/usr/bin/env python3
# Copyright (C) 2025-present Tom Müller - License: GNU General Public License v3
# This file is part of the Checkmk-sdp API client. It is subject to the terms and
# conditions defined in the file LICENSE or at <https://www.gnu.org/licenses/>.

from enum import Enum

import src.conf as conf


class PickHostState(Enum):
    UP = conf.SDP_HOST_UP_ID
    DOWN = conf.SDP_HOST_DOWN_ID
    UNREACH = conf.SDP_HOST_UNREACH_ID


class PickServiceState(Enum):
    OK = conf.SDP_SERVICE_OK_ID
    WARN = conf.SDP_SERVICE_WARN_ID
    CRITICAL = conf.SDP_SERVICE_CRITICAL_ID
    UNKNOWN = conf.SDP_SERVICE_UNKNOWN_ID


class PriorityEnum(Enum):
    HIGH = (4, "High", "#ff0000")
    MEDIUM = (3, "Medium", "#ff6600")
    NORMAL = (2, "Normal", "#006600")
    LOW = (1, "Low", "#666666")

    def __init__(self, id: int, name: str, color: str):
        self._id = id
        self._name = name
        self._color = color

    @property
    def id(self) -> int:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def color(self) -> str:
        return self._color

    def __str__(self):
        return self._name

