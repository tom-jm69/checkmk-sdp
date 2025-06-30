#!/usr/bin/env python3
# Copyright (C) 2025-present Tom Müller - License: GNU General Public License v3
# This file is part of the Checkmk-sdp API client. It is subject to the terms and
# conditions defined in the file LICENSE or at <https://www.gnu.org/licenses/>.

from src.app.utils import ResponseDetails


class SDPRequestFetchingError(Exception):
    """Is being raised, when we receive a error while we try to fetch a request"""

    pass


class SDPNoValidAuthentication(Exception):
    """Is being raised, when there is no valid authentication provided"""

    pass


class SDPRequestParsingError(Exception):
    """Is being raised, when we've failed to parse a SDP request"""

    pass


class SDPRequestAlreadyClosedError(Exception):
    """Is being raised, when we've tried to close a already closed SDP request"""

    pass


class SDPRequestClosingError(Exception):
    """Is being raised, when we run into a error while closing a request"""

    pass


class SDPViewRequestsParsingError(Exception):
    pass


class SDPRequestPollingError(Exception):
    pass


class SDPFetchRequestByID(Exception):
    pass


class SDPRequestCreationError(Exception):
    """Is being raised, when we've failed to create a SDP request"""

    def __init__(self, message: str = None, details: ResponseDetails = None):
        super().__init__(message)
        self.details = details


class SDPInvalidRequestDataError(SDPRequestCreationError):
    """Is being raised when we have invalid request data"""

    pass


class SDPBadResponseError(Exception):
    """Is being raised when we get a bad response from SDP"""

    def __init__(self, message: str = None, details: ResponseDetails = None):
        super().__init__(message)
        self.details = details


class SDPJSONParseError(Exception):
    def __init__(self, faulty_json: str = None):
        super().__init__(faulty_json)


class SDPUnreachableError(Exception):
    """Is being raised, when SDP is unreachable"""

    pass
