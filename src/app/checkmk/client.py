#!/usr/bin/env python3
# Copyright (C) 2025-present Tom Müller - License: GNU General Public License v3
# This file is part of the Checkmk-sdp API client. It is subject to the terms and
# conditions defined in the file LICENSE or at <https://www.gnu.org/licenses/>.

import asyncio
from typing import List

from src.app.utils.exceptions import BadResponseError, JSONParseError
from src.app.utils.models import ResponseDetails
from src.app.utils.wrapper import Wrapper

from .exceptions import (
    CheckmkHostFetchingError,
    CheckmkNoValidAuthenticationError,
    CheckmkServiceFetchingError,
)
from .models import (
    ColumnsRequest,
    HostAcknowledgement,
    HostComment,
    HostModel,
    ServiceAcknowledgement,
    ServiceComment,
    ServiceModel,
)


class Checkmk(Wrapper):
    """
    A client interface to interact with the Checkmk monitoring API.

    This class handles authentication, service and host retrieval, acknowledgment and comment management,
    and periodic polling, using asynchronous HTTP requests via aiohttp.

    Attributes:
        hosts (List[HostModel]): Cached list of monitored hosts.
        services (List[ServiceModel]): Cached list of monitored services.
        url (str): Checkmk server URL.
        port (int): Server port (default: 443).
        username (str): Username for authentication.
        secret (str): Password or API secret.
        timeout (int): Request timeout in seconds.
        retries (int): Retry count for polling attempts.
        site_name (str): Name of the Checkmk site.
        scheme (str): Connection scheme ('http' or 'https').
        verify_ssl (bool): Whether to verify SSL certificates.
        session (aiohttp.ClientSession): Shared aiohttp session.
        api_version (str): Target Checkmk API version.
        base_url (str): Constructed site URL.
        base_api_url (str): Constructed API root endpoint.
        background_tasks (List[asyncio.Task]): Polling background tasks.
        logger (Logger): Logger instance.
    """

    def __init__(
        self,
        url: str,
        verify_ssl: bool,
        site_name: str,
        username: str,
        secret: str,
        api_version: str,
        timeout=30,
        retries=5,
        port=443,
        scheme="http",
    ):
        """
        Initialize the Checkmk API client and configure authentication headers.

        Raises:
            NoValidAuthentication: If either the username or secret is missing.
        """
        super().__init__(
            url, secret, verify_ssl, timeout, retries, port, scheme, "Checkmk"
        )
        self.site_name = site_name
        self.username = username
        self.api_version = api_version
        self.base_url = f"{scheme}://{url}:{port}/{site_name}/check_mk"
        self.base_api_url = f"{self.base_url}/api/{api_version}"
        self.hosts = []
        self.services = []
        if username and secret:
            self.session.headers.update(
                {
                    "Authorization": f"Bearer {username} {secret}",
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                }
            )
        else:
            self.logger.error("No authentication credentials... Exiting.")
            raise CheckmkNoValidAuthenticationError(
                "No authentication credentials... Exiting."
            )

    async def start(self) -> None:
        await super().start()

        if not any(
            t.get_coro().__name__ == "poll_services_periodically"
            for t in self.background_tasks
        ):
            self.logger.info("Starting service polling task...")
            service_task = asyncio.create_task(self.poll_services_periodically())
            self.background_tasks.append(service_task)

        if not any(
            t.get_coro().__name__ == "poll_hosts_periodically"
            for t in self.background_tasks
        ):
            self.logger.info("Starting host polling task...")
            host_task = asyncio.create_task(self.poll_hosts_periodically())
            self.background_tasks.append(host_task)

    async def _get_services(self) -> ResponseDetails:
        """
        Send a request to retrieve all services from Checkmk.

        Returns:
            ResponseDetails: Structured response containing service data.

        Raises:
            CheckmkBadResponseError: On bad HTTP response status.
            CheckmkJSONParseError: If JSON parsing fails.
            CheckmkServiceFetchingError: For unexpected request errors.
        """
        columns_request_data = [
            "host_name",
            "description",
            "state",
            "last_check",
            "acknowledged",
            "acknowledgement_type",
            "check_command",
            "check_command_expanded",
            "check_flapping_recovery_notification",
            "check_freshness",
            "check_interval",
            "check_options",
            "check_period",
            "check_type",
            "checks_enabled",
            "execution_time",
            "flap_detection_enabled",
            "flappiness",
            "has_been_checked",
            "last_state",
            "last_state_change",
            "last_notification",
            "next_check",
            "next_notification",
            "notifications_enabled",
            "plugin_output",
            "long_plugin_output",
            "comments_with_extra_info",
        ]
        data = ColumnsRequest(columns=columns_request_data).model_dump_json()
        self.logger.debug("Sending service request to Checkmk")
        try:
            return await self._make_api_call(
                "post",
                "domain-types/service/collections/all",
                data=data,
            )
        except BadResponseError:
            raise
        except JSONParseError:
            raise
        except Exception as e:
            self.logger.exception(
                "Unexpected error while sending a request to get all services."
            )
            raise CheckmkServiceFetchingError("Failed to fetch services.") from e

    async def get_services(self) -> List[ServiceModel] | None:
        """
        Fetch and deserialize all services from the Checkmk API.

        Returns:
            List[ServiceModel] | None: List of services, or None on failure.

        Raises:
            CheckmkServiceFetchingError: On failed service request.
            CheckmkServiceParsingError: On invalid response structure.
        """
        try:
            raw_services = await self._get_services()

        except Exception:
            raise
        else:
            if not raw_services.success:
                return None
            services = [
                ServiceModel(**service)
                for service in raw_services.response_body["value"]
            ]
            return services

    async def get_hosts(self) -> List[HostModel] | None:
        """
        Fetch and deserialize all hosts from the Checkmk API.

        Returns:
            List[HostModel] | None: List of hosts, or None on failure.

        """
        try:
            raw_hosts = await self._get_hosts()
        except Exception:
            raise
        else:
            if not raw_hosts.success:
                return None
            hosts = [HostModel(**host) for host in raw_hosts.response_body["value"]]
            return hosts

    async def _get_hosts(self) -> ResponseDetails:
        """
        Send a request to retrieve all hosts from Checkmk.

        Returns:
            ResponseDetails: Structured response containing host data.

        Raises:
            BadResponseError: On bad HTTP response status.
            JSONParseError: If JSON parsing fails.
            CheckmkHostFetchingError: For unexpected request errors.
        """
        self.logger.debug("Sending host request to Checkmk")
        columns_request_data = [
            "name",
            "state",
            "last_check",
            "acknowledged",
            "acknowledgement_type",
        ]

        data = ColumnsRequest(columns=columns_request_data).model_dump_json()
        try:
            return await self._make_api_call(
                "post", "domain-types/host/collections/all", data=data
            )

        except BadResponseError:
            raise
        except JSONParseError:
            raise
        except Exception as e:
            self.logger.exception(
                "Unexpected error while sending a request to get all hosts."
            )
            raise CheckmkHostFetchingError("Failed to fetch hosts") from e

    async def _add_comment(
        self, comment_type: ServiceComment | HostComment
    ) -> ResponseDetails:
        """
        Submit a comment to either a service or host via Checkmk.

        Args:
            comment_type (ServiceComment | HostComment): The comment payload model.

        Returns:
            ResponseDetails: Result of the API call.
        """
        if isinstance(comment_type, ServiceComment):
            endpoint = "/domain-types/comment/collections/service"
        elif isinstance(comment_type, HostComment):
            endpoint = "/domain-types/comment/collections/host"
        return await self._make_api_call(
            method="post", endpoint=endpoint, data=comment_type.model_dump_json()
        )

    async def _add_acknowledgement(
        self, acknowledgement_payload: HostAcknowledgement | ServiceAcknowledgement
    ) -> ResponseDetails:
        """
        Submit an acknowledgment for a service or host.

        Args:
            acknowledgement_payload (HostAcknowledgement | ServiceAcknowledgement): Acknowledgment data.

        Returns:
            ResponseDetails: Result of the API call or a fake success for resolved problems.
        """
        if isinstance(acknowledgement_payload, ServiceAcknowledgement):
            endpoint = "/domain-types/acknowledge/collections/service"
            problem_state = await self._check_if_problem_state(acknowledgement_payload)
            if problem_state:
                return ResponseDetails(success=True)

        elif isinstance(acknowledgement_payload, HostAcknowledgement):
            endpoint = "/domain-types/acknowledge/collections/host"
            problem_state = await self._check_if_problem_state(acknowledgement_payload)
            if problem_state:
                return ResponseDetails(success=True)

        return await self._make_api_call(
            method="post",
            endpoint=endpoint,
            data=acknowledgement_payload.model_dump_json(),
        )

    async def _check_if_problem_state(
        self, acknowledgement_payload: HostAcknowledgement | ServiceAcknowledgement
    ) -> bool:
        """
        Check whether the given service or host is in a problem state.

        Args:
            acknowledgement_payload (HostAcknowledgement | ServiceAcknowledgement): Payload to evaluate.

        Returns:
            bool: True if in OK state (0), False otherwise.
        """
        if isinstance(acknowledgement_payload, ServiceAcknowledgement):
            for service in self.services:
                if (
                    service.extensions.check_command
                    == acknowledgement_payload.service_description
                ):
                    return service.extensions.state == 0
        elif isinstance(acknowledgement_payload, HostAcknowledgement):
            for host in self.hosts:
                if host.extensions.name == acknowledgement_payload.host_name:
                    return host.extensions.state == 0

    async def add_service_acknowledgement(
        self,
        service_check_command: str,
        hostname: str,
        comment: str,
        sticky: bool = True,
        persistent: bool = False,
        notify: bool = True,
    ) -> ResponseDetails:
        """
        Submit an acknowledgment for a Checkmk service.

        Args:
            service_check_command (str): Identifier for the service.
            hostname (str): Host on which the service runs.
            comment (str): Description/comment for the acknowledgment.
            sticky (bool): Whether acknowledgment persists across state changes.
            persistent (bool): Whether acknowledgment is saved persistently.
            notify (bool): Whether to notify users.

        Returns:
            ResponseDetails: API response result.
        """
        model = ServiceAcknowledgement(
            acknowledge_type="service",
            comment=comment,
            service_description=service_check_command,
            host_name=hostname,
            sticky=sticky,
            persistent=persistent,
            notify=notify,
        )
        result = await self._add_acknowledgement(model)
        return result

    async def add_host_acknowledgement(
        self,
        hostname: str,
        comment: str,
        sticky: bool = True,
        persistent: bool = False,
        notify: bool = True,
    ) -> ResponseDetails:
        """
        Submit an acknowledgment for a Checkmk host.

        Args:
            hostname (str): Host on which the service runs.
            comment (str): Description/comment for the acknowledgment.
            sticky (bool): Whether acknowledgment persists across state changes.
            persistent (bool): Whether acknowledgment is saved persistently.
            notify (bool): Whether to notify users.

        Returns:
            ResponseDetails: API response result.
        """
        model = HostAcknowledgement(
            acknowledge_type="host",
            comment=comment,
            host_name=hostname,
            sticky=sticky,
            persistent=persistent,
            notify=notify,
        )
        result = await self._add_acknowledgement(model)
        return result

    async def add_service_comment(
        self, service: str, hostname: str, comment: str, persistent: bool = True
    ) -> ResponseDetails:
        """
        Add a comment to a specific service in Checkmk.

        Args:
            service (str): The service description/name.
            hostname (str): The name of the host where the service resides.
            comment (str): The comment text to attach to the service.
            persistent (bool, optional): Whether the comment should persist across restarts. Defaults to True.

        Returns:
            ResponseDetails: The result of the API call indicating success or failure.
        """
        return await self._add_comment(
            ServiceComment(
                service_description=service,
                comment=comment,
                host_name=hostname,
                persistent=persistent,
            )
        )

    async def add_host_comment(
        self,
        hostname: str,
        comment: str,
        persistent: bool = True,
    ) -> ResponseDetails:
        """
        Add a comment to a specific host in Checkmk.

        Args:
            hostname (str): The name of the host to comment on.
            comment (str): The comment text to attach to the host.
            persistent (bool, optional): Whether the comment should persist across restarts. Defaults to True.

        Returns:
            ResponseDetails: The result of the API call indicating success or failure.
        """
        return await self._add_comment(
            HostComment(comment=comment, host_name=hostname, persistent=persistent)
        )

    async def get_host(self, hostname) -> dict:
        """
        Retrieve data for a specific host by hostname.

        Args:
            hostname (str): The name of the host to fetch.

        Returns:
            dict: The JSON response containing host details.

        Raises:
            aiohttp.ClientResponseError: On HTTP errors.
        """
        raise NotImplementedError()

    async def poll_hosts_periodically(self):
        retry_count = 0
        retry_interval_seconds = self.timeout

        while True:
            try:
                self.logger.debug("Polling hosts...")
                hosts = await self.get_hosts()
                if not hosts:
                    raise ValueError("Received empty hosts list.")

                retry_interval_seconds = self.timeout

            except Exception as e:
                retry_count += 1
                retry_interval_seconds *= 2
                self.logger.warning(
                    f"Polling hosts failed (attempt {retry_count}/{self.retries}): {e}"
                )
                if retry_count >= self.retries:
                    self.logger.critical(
                        f"Polling hosts failed {self.retries} times. "
                        f"Will continue after {self.timeout} seconds."
                    )
                    retry_count = 0

            else:
                self.hosts = hosts
                self.logger.info(f"Fetched {len(self.hosts)} hosts.")
                retry_count = 0

            await asyncio.sleep(self.timeout)

    async def poll_services_periodically(self):
        """
        Periodically poll the service API to update internal service state.

        Implements exponential backoff on failure and logs attempts and retries.

        Side Effects:
            Updates self.services with the latest fetched services.
            Logs polling activity and errors.
        """
        retry_count = 0
        retry_interval_seconds = self.timeout

        while True:
            try:
                self.logger.debug("Polling services...")
                services = await self.get_services()
                if not services:
                    raise ValueError("Received empty services list.")

                retry_interval_seconds = self.timeout

            except Exception as e:
                retry_count += 1
                retry_interval_seconds *= 2
                self.logger.warning(
                    f"Polling services failed (attempt {retry_count}/{self.retries}): {e}",
                )
                if retry_count >= self.retries:
                    self.logger.critical(
                        f"Polling services failed {self.retries} times in a row. "
                        f"Will continue trying after {self.timeout} seconds."
                    )
                    retry_count = 0

            else:
                self.services = services
                self.logger.info(f"Fetched {len(self.services)} services.")
                retry_count = 0
            await asyncio.sleep(self.timeout)

    async def activate_changes(self):
        """
        Triggers activation of any pending changes in Checkmk.

        Raises:
            NotImplementedError: Currently not implemented.
        """
        raise NotImplementedError()
