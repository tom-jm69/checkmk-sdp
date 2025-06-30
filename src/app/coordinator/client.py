#!/usr/bin/env python3
# Copyright (C) 2025-present Tom Müller - License: GNU General Public License v3
# This file is part of the Checkmk-sdp API client. It is subject to the terms and
# conditions defined in the file LICENSE or at <https://www.gnu.org/licenses/>.

import asyncio

from src.app.checkmk import Checkmk
from src.app.database import DB
from src.app.sdp import SDP
from src.app.utils import setup_logger


class LogicCoordinator:
    def __init__(
        self, sdp_client: SDP, checkmk_client: Checkmk, db: DB, check_interval: int = 10
    ):
        self.sdp = sdp_client
        self.checkmk = checkmk_client
        self.db = db
        self.logger = setup_logger(self.__class__.__name__)
        self.check_interval = check_interval

    async def start(self):
        """
        Starts our internal logic coordinator

        Returns
            None
        """
        while True:
            await self._process_request_states()

            await asyncio.sleep(self.check_interval)

    async def _process_request_states(self) -> None:
        """
        Processes request status and acknowledges checkmk alarms.

        Returns:
            None
        """

        def _log_and_skip(reason: str, request=None):
            self.logger.debug(f"Skipped {request} because {reason}")
            return

        for request in self.sdp.requests:
            self.logger.debug(f"Processing {request}")

            status_name = getattr(request.status, "name", None)
            if not status_name or status_name.lower() == "open":
                _log_and_skip("no status or status is open", request)
                continue

            if not request.id:
                _log_and_skip("no request id", request)
                continue

            checkmk_info = await self.db.get_checkmk_info(request.id)
            if not checkmk_info:
                _log_and_skip("no checkmk_info data", request)
                continue

            if checkmk_info.acknowledged == 1:
                _log_and_skip("already acknowledged", request)
                continue

            ack_comment = f"{self.sdp.ticket_url}{request.id}"
            response = None
            try:
                if checkmk_info.host_name:
                    if checkmk_info.service_check_command:
                        response = await self.checkmk.add_service_acknowledgement(
                            service_check_command=checkmk_info.service_description,
                            hostname=checkmk_info.host_name,
                            comment=ack_comment,
                        )
                    else:
                        response = await self.checkmk.add_host_acknowledgement(
                            hostname=checkmk_info.host_name,
                            comment=ack_comment,
                        )
            except Exception:
                self.logger.exception(
                    f"Failed to acknowledge {checkmk_info.service_check_command or checkmk_info.host_name}"
                )
                continue

            if response and response.success:
                self.logger.debug(
                    f"Acknowledged {checkmk_info.service_check_command or checkmk_info.host_name}"
                )
                try:
                    await self.db.update_checkmk_acknowledged(checkmk_info.id)
                    self.logger.debug(f"Acknowledgement updated for {checkmk_info.id}")
                except Exception as e:
                    self.logger.error(f"DB update failed: {e} for {checkmk_info.id}")

                try:
                    await self.db.insert_request(request.id, request.status.name)
                    self.logger.debug(f"Request {request.id} status updated in DB")
                except Exception as e:
                    self.logger.error(f"Request DB insert failed: {e} for {request.id}")
            else:
                self.logger.error(
                    f"Acknowledgement failed for {checkmk_info.model_dump_json()} request id {request.id} - {getattr(response, 'response_body', 'No response')}"
                )
