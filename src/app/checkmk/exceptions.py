#!/usr/bin/env python3
# Copyright (C) 2025-present Tom Müller - License: GNU General Public License v3
# This file is part of the Checkmk-sdp API client. It is subject to the terms and
# conditions defined in the file LICENSE or at <https://www.gnu.org/licenses/>.


class CheckmkServiceParsingError(Exception):
    """Is being raised, when a raw checkmk service object can't be properly parsed"""


class CheckmkServiceFetchingError(Exception):
    """Is being raised, when a checkmk service could not be fetched"""


class CheckmkHostFetchingError(Exception):
    """Is being raised, when a checkmk host could not be fetched"""


class CheckmkNoValidAuthenticationError(Exception):
    """Is being raised, when there is no valid authentication provided"""
