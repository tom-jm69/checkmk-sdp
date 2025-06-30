#!/usr/bin/env python3
# Copyright (C) 2025-present Tom Müller - License: GNU General Public License v3
# This file is part of the Checkmk-sdp API client. It is subject to the terms and
# conditions defined in the file LICENSE or at <https://www.gnu.org/licenses/>.

from fastapi import HTTPException
from pydantic import ValidationError

import src.conf as conf

from .app import FastAPI
from .checkmk.models import HostNotification, ServiceNotification
from .database.client import DB
from .database.exceptions import CheckmkDBInsertionError
from .sdp.client import SDP
from .sdp.exceptions import (
    SDPBadResponseError,
    SDPInvalidRequestDataError,
    SDPRequestCreationError,
    SDPUnreachableError,
)
from .sdp.models import NotificationResponse, PriorityEnum
from .sdp.models import Request as SDPRequest


async def handle_notification_request(
    *,
    checkmk_payload: ServiceNotification | HostNotification,
    sdp: SDP,
    app: FastAPI,
    db: DB,
    request_description: str = "This request has been created by checkmk.",
    impact_details: str = "None",
    resolution: str = "None",
) -> NotificationResponse:
    """
    Handle incoming Checkmk notifications and create an SDP request if needed.
    """
    logger = app.state.logger
    if is_recovery_notification(checkmk_payload):
        # host_last_problem_id could be used to resolve requests in sdp
        logger.debug(
            f"Received a recovery notification for host {checkmk_payload.host_name}"
        )
        return NotificationResponse(
            success=True, message="Recovery notification ignored.", request=None
        )

    cmk_db_id = await insert_checkmk_problem(db, checkmk_payload, logger)
    if not cmk_db_id:
        return NotificationResponse(
            success=False, message="No cmk_db_id. Insertion likely failed", request=None
        )

    existing_request_id = await db.check_if_request_exists(cmk_db_id)
    if existing_request_id:
        logger.info(
            f"Request {existing_request_id} already exists for problem ID {cmk_db_id}."
        )
        return NotificationResponse(
            success=True, message="Request already exists.", request=None
        )

    try:
        sdp_request = await create_sdp_request(
            sdp=sdp,
            payload=checkmk_payload,
            request_description=request_description,
            impact_details=impact_details,
            resolution=resolution,
            logger=logger,
        )
    except HTTPException as e:
        raise e
    else:
        sdp_db_id = await db.insert_request(sdp_request.id, sdp_request.status.name)
        if not sdp_db_id:
            return NotificationResponse(
                success=False,
                message="No sdp_db_id. Insertion likely failed",
                request=None,
            )
    try:
        await db.link_problem_and_request(cmk_db_id, sdp_db_id)
    except Exception as e:
        logger.exception(f"Failed to link problem with request: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to link problem with request in the database.",
        )

    return NotificationResponse(
        success=True,
        message="Request successfully created.",
        request=sdp_request,
    )


def is_recovery_notification(
    payload: ServiceNotification | HostNotification,
) -> bool:
    problem_id = getattr(payload, "service_problem_id", None) or getattr(
        payload, "host_problem_id", None
    )
    return problem_id == "0"


async def insert_checkmk_problem(
    db: DB, payload: ServiceNotification | HostNotification, logger
) -> int | None:
    try:
        return await db.insert_checkmk_problem(payload)
    except CheckmkDBInsertionError:
        logger.warning(
            "Database insertion error for problem tracking. Possible duplicate."
        )
        raise HTTPException(
            status_code=400,
            detail="Database insertion error for problem tracking. Problem might already exist.",
        )


async def create_sdp_request(
    *,
    sdp: SDP,
    payload: ServiceNotification | HostNotification,
    request_description: str,
    impact_details: str,
    resolution: str,
    logger,
) -> SDPRequest:
    is_service = isinstance(payload, ServiceNotification)

    subject = (
        f"Service Alert: {payload.service_desc}"
        if is_service
        else f"Host Alert: {payload.host_name}"
    )
    template_id = (
        conf.SDP_SERVICE_TEMPLATE_ID if is_service else conf.SDP_HOST_TEMPLATE_ID
    )

    try:
        result = await sdp.create_request(
            subject=subject,
            description=request_description,
            impact_details=impact_details,
            resolution=resolution,
            checkmk_payload=payload,
            template_id=template_id,
            priority=PriorityEnum.HIGH,
        )
    except SDPInvalidRequestDataError as e:
        logger.warning(f"Invalid request data: {e}")
        raise HTTPException(status_code=422, detail=str(e))
    except SDPBadResponseError as e:
        logger.error(f"Bad response from SDP: {e.details.response_body}")
        raise HTTPException(
            status_code=e.details.status_code or 502,
            detail=e.details.response_body,
        )
    except SDPUnreachableError:
        logger.critical("SDP is unreachable.")
        raise HTTPException(status_code=503, detail="SDP is unreachable.")
    except SDPRequestCreationError:
        logger.exception("Internal error during request creation.")
        raise HTTPException(
            status_code=500, detail="Internal error during request creation."
        )
    except Exception as e:
        logger.exception(f"Unexpected error during request creation: {e}")
        raise HTTPException(
            status_code=500, detail="Unexpected error during request creation."
        )

    return parse_sdp_response(result.response_body, logger)


def parse_sdp_response(response_body: dict, logger) -> SDPRequest:
    request_data = response_body.get("request")
    if not request_data:
        logger.error(f"Missing 'request' key in SDP response: {response_body}")
        raise HTTPException(status_code=500, detail="Malformed response from SDP.")

    try:
        return SDPRequest(**request_data)
    except ValidationError as e:
        logger.exception(f"Validation error while parsing SDP response: {e}")
        raise HTTPException(status_code=500, detail="Error parsing SDP response.")
