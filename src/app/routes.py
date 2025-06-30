#!/usr/bin/env python3
# Copyright (C) 2025-present Tom Müller - License: GNU General Public License v3
# This file is part of the Checkmk-sdp API client. It is subject to the terms and
# conditions defined in the file LICENSE or at <https://www.gnu.org/licenses/>.

from logging import Logger
from typing import cast

from fastapi import APIRouter, Depends, Request

from .auth import verify_token
from .checkmk.models import HostNotification, ServiceNotification
from .database.client import DB
from .notification import handle_notification_request
from .sdp.client import SDP

router = APIRouter()
# === Routes ===


@router.get("/ping", dependencies=[Depends(verify_token)])
async def ping():
    return {"ping": "pong"}


@router.post("/notify/service", dependencies=[Depends(verify_token)])
async def service_request(request: Request, payload: ServiceNotification):
    sdp = cast(SDP, request.app.state.sdp)
    db = cast(DB, request.app.state.db)
    logger = cast(Logger, request.app.state.logger)
    logger.info(f"Received service alert for: '{payload.host_name}'")
    logger.debug(f"Received the following service payload: {payload}")
    return await handle_notification_request(
        app=request.app,
        sdp=sdp,
        db=db,
        checkmk_payload=payload,
    )


@router.post("/notify/host", dependencies=[Depends(verify_token)])
async def host_request(request: Request, payload: HostNotification):
    sdp = cast(SDP, request.app.state.sdp)
    db = cast(DB, request.app.state.db)
    logger = cast(Logger, request.app.state.logger)
    logger.info(f"Received host alert for: '{payload.host_name}'")
    logger.debug(f"Received the following host payload: {payload}")
    return await handle_notification_request(
        app=request.app,
        sdp=sdp,
        db=db,
        checkmk_payload=payload,
    )
