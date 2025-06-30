#!/usr/bin/env python3
# Copyright (C) 2025-present Tom Müller - License: GNU General Public License v3
# This file is part of the Checkmk-sdp API client. It is subject to the terms and
# conditions defined in the file LICENSE or at <https://www.gnu.org/licenses/>.


import asyncio
import json
from contextlib import suppress
from typing import Self

import aiohttp
from aiohttp import ClientTimeout, TCPConnector

from src.app.utils.log import setup_logger
from src.app.utils.models import ResponseDetails

from .exceptions import BadResponseError, JSONParseError


class Wrapper:
    def __init__(
        self,
        url: str,
        secret: str,
        verify_ssl: bool,
        timeout: int,
        retries: int,
        port: int,
        scheme: str,
        name: str,
    ):
        self.url = url
        self.port = port
        self.secret = secret
        self.timeout = timeout
        self.retries = retries
        self.verify_ssl = verify_ssl
        self.scheme = scheme
        self.session = aiohttp.ClientSession(
            timeout=ClientTimeout(timeout),
            connector=TCPConnector(verify_ssl=verify_ssl),
        )
        self.background_tasks = []
        self.__class__.__name__ = name
        self.logger = setup_logger(self.__class__.__name__)
        self.logger.debug(f"{self.__class__.__name__} initialized with URL: {url}")

    async def start(self) -> None:
        # Clean up finished tasks
        self.background_tasks = [t for t in self.background_tasks if not t.done()]
        await self.add_background_tasks()

    async def add_background_tasks(self):
        # Intended to be overridden in subclasses
        pass

    async def close(self) -> None:
        self.logger.info("Shutting down client...")

        if self.background_tasks:
            self.logger.info("Cancelling background polling tasks...")
            for task in self.background_tasks:
                task.cancel()
            for task in self.background_tasks:
                with suppress(asyncio.CancelledError):
                    await task
            self.logger.info("All background polling tasks stopped.")

        await self.session.close()
        self.logger.info("HTTP session closed.")

    async def __aenter__(self) -> Self:
        """
        Enter the async context manager.

        Returns:
            Self: The current instance.
        """
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        """
        Exit the async context manager and close the session.

        Args:
            exc_type: Exception type if raised.
            exc: Exception instance if raised.
            tb: Traceback object if exception occurred.

        Returns
            None
        """

        if tb:
            self.logger.debug(f"Exited with {exc}")
        await self.session.close()

    async def _http_get(self, endpoint: str, params: dict = None) -> ResponseDetails:  # type: ignore
        """
        Perform an HTTP GET request to the specified API endpoint.

        Args:
            endpoint (str): The relative API endpoint to send the GET request to.
            params (dict, optional): Query parameters to include in the request.

        Returns:
            ResponseDetails: The structured response from the API call.
        """
        return await self._make_api_call("get", endpoint, params=params)

    async def _http_post(
        self, endpoint: str, data: dict | str = None
    ) -> ResponseDetails:  # type: ignore
        """
        Perform an HTTP POST request to the specified API endpoint.

        Args:
            endpoint (str): The relative API endpoint to send the POST request to.
            data (dict | str, optional): Payload to include in the request body.

        Returns:
            ResponseDetails: The structured response from the API call.
        """
        return await self._make_api_call("post", endpoint, data=data)

    async def _http_put(
        self, endpoint: str, data: dict | str = None
    ) -> ResponseDetails:  # type: ignore
        """
        Perform an HTTP PUT request to the specified API endpoint.

        Args:
            endpoint (str): The relative API endpoint to send the PUT request to.
            data (dict | str, optional): Payload to update the resource.

        Returns:
            ResponseDetails: The structured response from the API call.
        """
        return await self._make_api_call("put", endpoint, data=data)

    async def _http_delete(self, endpoint: str) -> ResponseDetails:
        """
        Perform an HTTP DELETE request to the specified API endpoint.

        Args:
            endpoint (str): The relative API endpoint to send the DELETE request to.

        Returns:
            ResponseDetails: The structured response from the API call.
        """
        return await self._make_api_call("delete", endpoint)

    async def _make_api_call(
        self, method: str, endpoint: str, **kwargs
    ) -> ResponseDetails:
        """
        Perform a generic asynchronous API call using aiohttp.

        This method dynamically calls the appropriate HTTP method (GET, POST, PUT, DELETE, etc.)
        on the aiohttp session object. It builds the full request URL from the base API URL and
        handles response parsing and exception management.

        Args:
            method (str): The HTTP method to use ('get', 'post', 'put', 'delete', etc.).
            endpoint (str): The API endpoint to call, appended to the base API URL.
            **kwargs: Additional arguments to pass to the aiohttp request method
                      (e.g., params, json, data, headers).

        Returns:
            ResponseDetails: The parsed and structured response from the API call.

        Raises:
            aiohttp.ClientConnectionError: For network connectivity issues.
            aiohttp.ClientConnectorError: For connection setup failures.
            asyncio.TimeoutError: If the request times out.
            BadResponseError: For known application-level response issues.
            JSONParseError: If the response cannot be parsed as expected.
            Exception: For any other unexpected errors, with logging for diagnostics.
        """
        self.logger.debug(
            f"Calling _make_api_call with method={method}, endpoint={endpoint}, kwargs={kwargs}"
        )
        url = f"{self.base_api_url}/{endpoint.lstrip('/')}"
        try:
            async with getattr(self.session, method)(url, **kwargs) as response:
                parsed_response = await self._parse_response(response, endpoint)
                return parsed_response
        except (
            aiohttp.ClientConnectionError,
            aiohttp.ClientConnectorError,
            asyncio.TimeoutError,
            BadResponseError,
            JSONParseError,
        ):
            raise
        except Exception:
            self.logger.exception("Unhandled exception in _make_api_call")
            raise

    async def _parse_response(
        self, response: aiohttp.ClientResponse, endpoint: str
    ) -> ResponseDetails:
        """
        Safely parse the aiohttp response, handling 204 No Content and unexpected content types.

        This method reads the response body, checks for valid content types,
        handles edge cases such as HTTP 204 responses, and raises custom exceptions
        in case of errors or unexpected responses.

        Args:
            response (aiohttp.ClientResponse): The HTTP response object returned by aiohttp.
            endpoint (str): The API endpoint that was called, used for context in logging or errors.

        Returns:
            ResponseDetails: A structured object containing parsed response data, status, and metadata.

        Raises:
            JSONParseError: If the response couldn't be properly json encoded.
        """
        status_code = response.status
        success = status_code in {200, 201, 204}
        response_body = None
        content_type = response.headers.get("Content-Type", "")
        try:
            if status_code == 204:
                response_body = None
            elif (
                "application/json" in content_type
                or "application/problem+json" in content_type
            ):
                response_body = await response.json()
            else:
                response_body = await response.text()
                self.logger.warning(
                    f"Received unexpected Content-Type ({content_type}) from {endpoint}, "
                    f"but treating as success due to status {status_code}"
                )
        except (aiohttp.ContentTypeError, json.JSONDecodeError) as e:
            text = await response.text()
            self.logger.error("Failed to parse JSON from response", exc_info=True)
            raise JSONParseError(faulty_json=str({"raw": text})) from e

        if not success:
            return ResponseDetails(
                status_code=status_code,
                response_body=response_body,
                endpoint=endpoint,
                success=False,
            )

        self.logger.debug(
            f"Successfully parsed JSON response from {endpoint}: {response_body}"
        )

        return ResponseDetails(
            status_code=status_code,
            response_body=response_body,
            endpoint=endpoint,
            success=success,
        )
