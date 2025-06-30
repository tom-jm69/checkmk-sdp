#!/usr/bin/env python3
# Copyright (C) 2025-present Tom Müller - License: GNU General Public License v3
# This file is part of the Checkmk-sdp API client. It is subject to the terms and
# conditions defined in the file LICENSE or at <https://www.gnu.org/licenses/>.

from typing import Dict, Optional

from dateutil.tz import gettz
from pydantic import BaseModel

tzinfos = {
    "CEST": gettz("Europe/Berlin"),
    "CET": gettz("Europe/Berlin"),  # for winter time
}


class ResponseDetails(BaseModel):
    status_code: Optional[int] = None
    response_body: Optional[Dict] = None
    endpoint: Optional[str] = None
    success: Optional[bool] = None
