#!/usr/bin/env python3
# Copyright (C) 2025-present Tom Müller - License: GNU General Public License v3
# This file is part of the Checkmk-sdp API client. It is subject to the terms and
# conditions defined in the file LICENSE or at <https://www.gnu.org/licenses/>.

import asyncio
import json
from typing import List

from pydantic import BaseModel, ValidationError

from src.app.checkmk.models import HostNotification, ServiceNotification
from src.app.utils.exceptions import BadResponseError, JSONParseError
from src.app.utils.models import ResponseDetails
from src.app.utils.wrapper import Wrapper

from .enums import PickHostState, PickServiceState
from .exceptions import (
    SDPInvalidRequestDataError,
    SDPNoValidAuthentication,
    SDPRequestAlreadyClosedError,
    SDPRequestClosingError,
    SDPRequestCreationError,
    SDPRequestFetchingError,
    SDPUnreachableError,
    SDPViewRequestsParsingError,
)
from .models import (
    CloseRequest,
    ClosureCode,
    ClosureInfo,
    CreationRequest,
    CreationRequestDataModel,
    HostTemplateFields,
    IncidentTemplateResponse,
    PickField,
    Request,
    RequestPriority,
    RequestType,
    Resolution,
    ServiceTemplateFields,
    Status,
    Template,
    TimeValueSDP,
    User,
    ViewRequestsDataModel,
)


class SDP(Wrapper):
    """
    Asynchronous client for interacting with the ServiceDesk Plus (SDP) REST API.

    Handles operations such as request creation, retrieval, template fetching,
    and periodic polling of requests.

    Attributes:
        url (str): Base hostname or IP of the SDP instance.
        port (int): Port used for communication with SDP.
        secret (str): Authentication token for API access.
        timeout (int): Timeout duration for requests in seconds.
        retries (int): Max number of retries for polling logic.
        requester_name (str): Default requester name used in ticket creation.
        requester_id (int): ID for the default requester.
        verify_ssl (bool): Toggle for SSL certificate verification.
        session (aiohttp.ClientSession): Persistent HTTP session for requests.
        api_version (str): API version for endpoint construction.
        api_base_url (str): Constructed base URL for API calls.
        logger (Logger): Logger instance for debugging and error tracking.
    """

    def __init__(
        self,
        url,
        secret,
        verify_ssl,
        api_version,
        timeout=20,
        retries=5,
        port=8443,
        scheme="http",
        requester_name="checkmk",
        requester_id=604,
    ):
        """
        Initialize an SDP client instance for interacting with the ServiceDesk Plus API.

        Args:
            url (str): The hostname or IP of the SDP instance (without scheme or port).
            secret (str): Authentication token used for API authorization.
            verify_ssl (bool): Whether to verify the SSL certificate.
            api_version (str): API version string (e.g., "v3").
            timeout (int, optional): Request timeout in seconds. Defaults to 20.
            retries (int, optional): Maximum number of retries for polling. Defaults to 5.
            port (int, optional): Port to connect to. Defaults to 8443.
            scheme (str, optional): HTTP scheme to use ("http" or "https"). Defaults to "http".
            requester_name (str, optional): Name of the requester for created tickets. Defaults to "checkmk".
            requester_id (int, optional): ID of the requester. Defaults to 604.

        Raises:
            NoValidAuthentication: If the `secret` is not provided.
        """
        super().__init__(
            url, secret, verify_ssl, timeout, retries, port, scheme, "Service Desk Plus"
        )
        self.url: str = url
        self.port: int = port
        self.secret: str = secret
        self.timeout: int = timeout
        self.retries: int = retries
        self.requester_name: str = requester_name
        self.requester_id: int = requester_id
        self.verify_ssl: bool = verify_ssl
        self.api_version = api_version
        self.base_api_url = f"{scheme}://{url}:{port}/api/{api_version}"
        self.ticket_url = f"{scheme}://{url}:{port}/WorkOrder.do?woMode=viewWO&woID="
        self.requests = []
        if secret:
            self.session.headers.update(
                {
                    "authtoken": f"{secret}",
                }
            )
        else:
            self.logger.error("No authentication credentials... Exiting.")
            raise SDPNoValidAuthentication("No authentication credentials... Exiting.")

    async def start(self) -> None:
        await super().start()

        if not any(
            t.get_coro().__name__ == "poll_services_periodically"
            for t in self.background_tasks
        ):
            self.logger.info("Starting service polling task...")
            service_task = asyncio.create_task(self.poll_requests_periodically())
            self.background_tasks.append(service_task)

    async def get_templates(self) -> dict:
        """
        Fetches all available request templates from SDP.

        Returns:
            dict: JSON response from the API.
        """
        raise NotImplementedError()
        endpoint = f"{self.base_url}/request_templates"
        async with self.session.get(endpoint) as response:
            data = await response.json()
            return data

    async def get_template_by_id(self, template_id: int) -> IncidentTemplateResponse:
        """
        Retrieve a specific request template by its ID.

        Args:
            template_id (int): Template identifier.

        Returns:
            IncidentTemplateResponse: Parsed template response.

        Raises:
            RequestParsingError: If response contains invalid JSON.
            InvalidRequestData: If validation of response fails.
            SDPUnreachableError: For network or server errors.
        """
        raise NotImplementedError()

    async def create_request(
        self,
        subject: str,
        description: str,
        resolution: str,
        impact_details: str,
        checkmk_payload: ServiceNotification | HostNotification,
        template_id: int,
        priority: RequestPriority,
        request_type: str = "Incident",
        ticket_status: str = "Open",
    ) -> ResponseDetails | None:
        """
        Create a new request in SDP using a predefined template and Checkmk payload.

        Args:
            subject (str): Subject/title of the request.
            description (str): Description of the issue.
            resolution (str): Resolution summary.
            impact_details (str): Details about the impact of the issue.
            checkmk_payload (ServiceNotification | HostNotification): Source notification.
            template_id (int): Template ID to use for request.
            request_type (str): Type of the request. Default is "Incident".
            ticket_status (str): Initial status of the ticket. Default is "Open".

        Returns:
            dict: API response payload on successful creation.

        Raises:
            RequestCreationError: For construction or sending issues.
        """

        self.logger.debug(
            f"Creating request for subject='{subject}' with template_id={template_id}"
        )
        try:
            request_model = self._build_request_model(
                subject=subject,
                description=description,
                resolution=resolution,
                impact_details=impact_details,
                request_type=request_type,
                ticket_status=ticket_status,
                checkmk_payload=checkmk_payload,
                template_id=template_id,
                priority=priority,
            )
            payload = self._serialize_payload(
                model=CreationRequestDataModel(request=request_model)
            )
            if not payload:
                raise JSONParseError("Failed to serialize the request_model")
            return await self._send_request(payload)
        except JSONParseError:
            raise
        except Exception:
            self.logger.exception("Unexpected error during request creation.")
            raise

    def _build_request_model(
        self,
        subject: str,
        description: str,
        resolution: str,
        impact_details: str,
        request_type: str,
        ticket_status: str,
        template_id: int,
        checkmk_payload: ServiceNotification | HostNotification,
        priority: RequestPriority,
    ) -> CreationRequest:
        """
        Build the internal request model using Checkmk payload and provided metadata.

        Returns:
            CreationRequest: Structured model for the request.

        Raises:
            InvalidRequestData: If model validation fails.
            RequestCreationError: For unknown failures during model construction.
        """
        self.logger.debug("Building request model")
        try:
            request_prio = RequestPriority.from_enum(priority)
            if isinstance(checkmk_payload, ServiceNotification):
                """service template"""
                state = PickField(
                    name=checkmk_payload.service_state,
                    id=PickServiceState[checkmk_payload.service_state].value,
                )
                fields = ServiceTemplateFields(
                    servicename=checkmk_payload.service_name,
                    servicecheckcommand=checkmk_payload.service_check_command,
                    servicestatus=state,
                    serviceoutput=checkmk_payload.service_output_short,
                    serviceoutputlong=checkmk_payload.service_output_long,
                    servicedescription=checkmk_payload.service_desc,
                    servicelaststatechange=TimeValueSDP(
                        value=int(
                            checkmk_payload.service_last_state_change.timestamp() * 1000
                        )  # convert to millis
                    ),
                    serviceurl=checkmk_payload.service_url,
                    hostname=checkmk_payload.host_name,
                    hostalias=checkmk_payload.host_alias,
                    hostipv4=checkmk_payload.host_ipv4,
                    hoststate=PickField(name=checkmk_payload.host_state),
                    hosturl=checkmk_payload.host_url,
                    contacts=checkmk_payload.contacts,
                    alarmdate=TimeValueSDP(
                        value=int(
                            checkmk_payload.notification_datetime_long.timestamp()
                            * 1000
                        )  # convert to millis
                    ),
                )  # type: ignore
            elif isinstance(checkmk_payload, HostNotification):
                """host template"""
                state = PickField(
                    name=checkmk_payload.host_state,
                    id=PickHostState[checkmk_payload.host_state].value,
                )
                fields = HostTemplateFields(
                    hoststate=state,
                    hostipv4=checkmk_payload.host_ipv4,
                    hostname=checkmk_payload.host_name,
                    hostalias=checkmk_payload.host_alias,
                    hosturl=checkmk_payload.host_url,
                    hostoutput=checkmk_payload.host_output,
                    contacts=checkmk_payload.contacts,
                    hostlaststatechange=TimeValueSDP(
                        value=int(
                            checkmk_payload.host_last_state_change.timestamp() * 1000
                        ),  # convert to millis
                    ),
                    alarmdate=TimeValueSDP(
                        value=int(
                            checkmk_payload.notification_datetime_long.timestamp()
                            * 1000
                        ),  # convert to millis
                    ),
                    hostlaststateup=TimeValueSDP(
                        value=int(
                            checkmk_payload.host_last_up.timestamp() * 1000
                        )  # convert to millis
                    ),
                )  # type: ignore
            model = CreationRequest(
                subject=f"{subject} - {state.name}",
                description=description,
                requester=User(id=self.requester_id, name=self.requester_name),
                resolution=Resolution(content=resolution),
                impact_details=impact_details,
                status=Status(name=ticket_status),
                request_type=RequestType(name=request_type),
                template=Template(id=template_id),
                udf_fields=fields,
                priority=request_prio,
            )
            self.logger.debug(f"Built CreationRequest model: {model}")
            return model
        except ValidationError as e:
            self.logger.exception("Validation failed in CreationRequest model")
            raise SDPInvalidRequestDataError("Invalid request data.") from e
        except UnboundLocalError as e:
            self.logger.exception("Accessed a non existing variable")
            raise SDPInvalidRequestDataError("Invalid request data.") from e
        except Exception:
            self.logger.exception("Unexpected error constructing CreationRequest.")
            raise SDPRequestCreationError("Unexpected model construction error.")

    def _serialize_payload(
        self, model: BaseModel, *, exclude_none: bool = True, by_alias: bool = True
    ) -> str:
        """
        Serialize a Pydantic model to JSON.

        Args:
            model (BaseModel): Any Pydantic model to serialize.
            exclude_none (bool): Whether to exclude None values. Default is True.
            by_alias (bool): Whether to use field aliases. Default is True.

        Returns:
            str: Serialized JSON string.

        Raises:
            SDPRequestCreationError: On serialization failure.
        """
        self.logger.debug(f"Serializing payload for model: {model.__class__.__name__}")
        try:
            payload = model.model_dump_json(
                exclude_none=exclude_none, by_alias=by_alias
            )
            self.logger.debug(f"Serialized payload: {payload}")
            return payload
        except Exception:
            self.logger.exception(
                f"Failed to serialize model: {model.__class__.__name__}"
            )
            raise SDPRequestCreationError(
                f"Payload serialization failed for {model.__class__.__name__}"
            )

    async def _send_request(self, payload: str) -> ResponseDetails:
        """
        Send the serialized request payload to SDP.

        Args:
            payload (str): JSON-formatted input data.

        Returns:
            aiohttp.ClientResponse: Parsed JSON response.
        """
        self.logger.debug("Sending request to SDP")
        try:
            return await self._make_api_call(
                "post", "requests", data={"input_data": payload}
            )
        except BadResponseError:
            raise
        except SDPUnreachableError:
            raise
        except Exception as e:
            self.logger.exception("Unexpected error while sending request.")
            raise SDPRequestCreationError("Failed to create request.") from e

    async def _close_request(self, payload: str, request_id: int) -> ResponseDetails:
        """
        Send the serialized request payload to SDP.

        Args:
            payload (str): JSON-formatted input data.

        Returns:
            aiohttp.ClientResponse: Parsed JSON response.
        """
        try:
            return await self._make_api_call(
                "put", f"requests/{request_id}/close", data={"input_data": payload}
            )
        except BadResponseError:
            raise
        except SDPUnreachableError:
            raise
        except Exception as e:
            self.logger.exception("Unexpected error while closing request.")
            raise SDPRequestClosingError("Failed to close request.") from e

    async def close_request(
        self,
        request_id: int,
        requester_ack_comments: str = "Checkmk alarm has been resolved.",
        closure_comments: str = "Request closed by checkmk.",
        requester_ack_resolution: bool = True,
    ) -> ResponseDetails:
        """
        Close a request by ID.

        Args:
            request_id (int): The ID of the request to close.
            requester_ack_comments (str): Comment from requester.
            closure_comments (str): Final closure note.

        Returns:
            bool: True if closed, False if already closed.

        Raises:
            SDPRequestCreationError: On unexpected failure.
        """
        self.logger.debug(f"Attempting to close request {request_id}")
        try:
            request_model = CloseRequest(
                request={
                    "closure_info": ClosureInfo(
                        requester_ack_comments=requester_ack_comments,
                        closure_comments=closure_comments,
                        closure_code=ClosureCode(name="Success"),
                        requester_ack_resolution=requester_ack_resolution,
                    )
                }
            )
            payload = self._serialize_payload(model=request_model)
            return await self._close_request(payload, request_id)

        except BadResponseError as e:
            msg = str(e.details.response_body if e.details else "")
            if "already closed" in msg.lower():
                self.logger.warning(f"Request '{request_id}' is already closed.")
                raise SDPRequestAlreadyClosedError()
            self.logger.error(
                f"Bad response while closing request {request_id}: {msg}", exc_info=True
            )
            raise

        except SDPUnreachableError:
            raise

        except Exception as e:
            self.logger.exception("Unexpected error while trying to close a request.")
            raise SDPRequestCreationError("Failed to close request.") from e

    async def get_requests_by_id(self, request_ids: List[str]) -> List[dict]:
        """
        Fetch multiple requests concurrently by their IDs.

        Args:
            request_ids (List[str]): List of request IDs.

        Returns:
            List[dict]: Successfully retrieved request data.
        """
        self.logger.debug(f"Fetching requests by ID: {request_ids}")
        tasks = [self._fetch_single_request(request_id) for request_id in request_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        successful = []
        for request_id, result in zip(request_ids, results):
            if isinstance(result, Exception):
                self.logger.error(f"Error fetching request {request_id}: {str(result)}")
            else:
                successful.append(result)

        return successful

    async def poll_requests_periodically(self):
        """
        Periodically polls the SDP API to fetch requests with retry and backoff logic.

        Side Effects:
            Updates internal `self.requests` and logs activity.
        """
        self.logger.debug("Starting periodic polling loop")
        retry_count = 0
        had_failures = False

        while True:
            self.logger.debug(f"Polling attempt {retry_count}")
            try:
                self.logger.debug("Polling requests...")
                requests = await self.get_all_requests()

                if not requests:
                    raise ValueError("Received empty request list.")

            except Exception as e:
                retry_count += 1
                had_failures = True
                self.logger.warning(
                    f"Polling failed (attempt {retry_count}/{self.retries}): {e}",
                )

                if retry_count >= self.retries:
                    self.logger.critical(
                        f"Polling failed {self.retries} times in a row. "
                        f"Will continue trying after {self.timeout} seconds."
                    )
                    retry_count = 0
            else:
                self.requests = requests
                self.logger.info(f"Fetched {len(requests)} incident requests.")

                if had_failures:
                    self.logger.info(
                        f"Polling succeeded after {retry_count} failed attempt(s)."
                    )

                retry_count = 0
                had_failures = False

            await asyncio.sleep(self.timeout)

    async def get_all_requests(
        self,
        row_count: int = 100,
        sort_field: str = "last_updated_time",
        sort_order: str = "desc",
    ) -> List[Request] | List:
        """
        Fetch all requests in the system using paginated queries.

        Args:
            row_count (int): Number of entries per page. Default is 100.
            sort_field (str): Field to sort by. Default is "created_time".
            sort_order (str): Sorting direction. Default is "asc".

        Returns:
            List[Request]: List of parsed Request objects.

        Raises:
            RequestFetchingError: On any failure during fetch or parsing.
        """
        self.logger.debug("Fetching all requests")
        try:
            ids = await self._fetch_all_request_ids(row_count, sort_field, sort_order)
        except Exception as e:
            self.logger.error("Failed to fetch request IDs.")
            raise SDPRequestFetchingError("Fetching request IDs failed.") from e

        if not ids:
            return []

        try:
            data = await self.get_requests_by_id(ids)
            requests = [
                Request(**request.response_body["request"]) for request in data or []
            ]
            return requests
        except Exception as e:
            self.logger.error("Failed to fetch detailed requests.", exc_info=True)
            raise SDPRequestFetchingError("Fetching detailed requests failed.") from e

    async def _fetch_all_template_ids(
        self, row_count: int, sort_field: str, sort_order: str
    ) -> List[str]:
        """
        Placeholder for fetching all template IDs (not implemented).

        Raises:
            NotImplementedError
        """
        raise NotImplementedError()

    async def _fetch_single_request(self, request_id: str) -> ResponseDetails:
        """
        Fetch a single request's details by ID.

        Args:
            request_id (str): The ID of the request.

        Returns:
            dict: Request data as JSON.

        Raises:
            RequestFetchingError: On non-200 responses.
            RequestParsingError: On invalid JSON response.
        """
        self.logger.debug(f"Fetching single request ID: {request_id}")
        try:
            return await self._make_api_call("get", f"requests/{request_id}")
        except BadResponseError:
            raise
        except SDPUnreachableError:
            raise
        except Exception as e:
            self.logger.exception(f"Error fetching request {request_id}")
            raise SDPRequestFetchingError(f"Error fetching request {request_id}") from e

    async def _fetch_all_request_ids(
        self, row_count: int, sort_field: str, sort_order: str
    ) -> List[str]:
        """
        Internal method to collect all request IDs using pagination.

        Args:
            row_count (int): Entries per page.
            sort_field (str): Sort field.
            sort_order (str): Sort order.

        Returns:
            List[str]: All collected request IDs.

        Raises:
            ViewRequestsParsingError: On serialization or payload creation error.
            RequestParsingError: If API returns invalid JSON.
        """
        self.logger.debug("Fetching all request IDs with pagination")
        ids = []
        start_index = 0

        while True:
            try:
                model = ViewRequestsDataModel(
                    row_count=row_count,
                    start_index=start_index,
                    sort_field=sort_field,
                    sort_order=sort_order,
                    get_total_count=True,
                )
                params = {
                    "input_data": json.dumps(
                        {"list_info": model.model_dump(exclude_none=True)}
                    )
                }
            except Exception as e:
                self.logger.error("Invalid ViewRequestsDataModel", exc_info=True)
                raise SDPViewRequestsParsingError() from e

            try:
                data = await self._make_api_call("get", "requests", params=params)
            except BadResponseError:
                raise
            except SDPUnreachableError:
                raise
            except Exception as e:
                self.logger.error("Failed to fetch request IDs", exc_info=True)
                raise SDPRequestFetchingError("Failed to fetch request IDs.") from e
            requests_data = data.response_body.get("requests", [])
            if not requests_data:
                break

            self.logger.debug(
                f"Fetched page: start_index={start_index}, retrieved_ids={len(requests_data)}"
            )
            ids.extend(r["id"] for r in requests_data)

            if not data.response_body.get("list_info", {}).get("has_more_rows", False):
                break
            start_index += row_count

        return ids
