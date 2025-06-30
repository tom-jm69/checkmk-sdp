#!/usr/bin/env python3
# Copyright (C) 2025-present Tom Müller - License: GNU General Public License v3
# This file is part of the Checkmk-sdp API client. It is subject to the terms and
# conditions defined in the file LICENSE or at <https://www.gnu.org/licenses/>.

from .models import ResponseDetails


class JSONParseError(Exception):
    def __init__(self, faulty_json: str = None):
        super().__init__(faulty_json)


class BadResponseError(Exception):
    """Is being raised when we get a bad response from Checkmk"""

    def __init__(self, message: str = None, details: ResponseDetails = None):
        super().__init__(message)
        self.details = details
