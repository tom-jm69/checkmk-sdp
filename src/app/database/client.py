#!/usr/bin/env python3
# Copyright (C) 2025-present Tom Müller - License: GNU General Public License v3
# This file is part of the Checkmk-sdp API client. It is subject to the terms and
# conditions defined in the file LICENSE or at <https://www.gnu.org/licenses/>.

import asyncio
import os
import sqlite3
from contextlib import asynccontextmanager, suppress
from logging import Logger
from typing import AsyncGenerator

import asqlite

from src.app.checkmk import HostNotification, ServiceNotification
from src.app.utils import setup_logger

from .exceptions import CheckmkDBInsertionError
from .models import CheckmkInfo, CombinedRequest


class DB:
    def __init__(self, db_name: str, db_path: str, db_scheme_basepath: str):
        """
        Initialize the DB class for interacting with an SQLite database.

        Args:
            db_name (str): The name of the database file (without extension).
            db_path (str): The path where the database file is located.
            db_scheme_basepath (str): The directory path containing SQL schema files.
        """
        self.db_name = db_name
        self.db_path = db_path
        self.db_scheme_basepath = db_scheme_basepath
        self.pool = asqlite.create_pool(f"{db_path}/{db_name}.sqlite3")
        self.logger = setup_logger("Database")
        self.problem_cache = ProblemCache(logger=self.logger)
        self.background_task = None

    async def poll_problemids_periodically(self):
        """
        Periodically fetches all problem ids from the database.

        Side Effects:
            Updates internal `self.problem_cache` and logs activity.
        """
        self.logger.debug("Starting periodic polling loop")
        self.retries = 5
        self.timeout = 10
        retry_count = 0
        had_failures = False

        while True:
            self.logger.debug(f"Polling attempt {retry_count}")
            try:
                self.logger.debug("Polling problem id cache...")
                await self.problem_cache.refresh_cache(self)

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
                if had_failures:
                    self.logger.info(
                        f"Polling succeeded after {retry_count} failed attempt(s)."
                    )

                retry_count = 0
                had_failures = False

            await asyncio.sleep(self.timeout)

    async def start(self) -> None:
        """
        Starts the client and its background fetching task.
        """
        await self.create_tables()
        if self.background_task is None or self.background_task.done():
            self.logger.info("Starting background polling task...")
            self.background_task = asyncio.create_task(
                self.poll_problemids_periodically()
            )
            self.logger.info("Started background polling task.")
        else:
            self.logger.warning("Background task already running.")

    async def close(self) -> None:
        """
        Gracefully shuts down the client and background polling.
        """
        self.logger.info("Shutting down pool...")

        if self.background_task:
            self.logger.info("Cancelling background polling task...")
            self.background_task.cancel()
            with suppress(asyncio.CancelledError):
                await self.background_task
            self.logger.info("Background polling task stopped.")

        async with self.pool as pool:
            await pool.close()
        self.logger.info("Database pool closed.")

    @asynccontextmanager
    async def get_cursor(self) -> AsyncGenerator:
        """
        Provide a context-managed database cursor for executing SQL commands.

        Yields:
            asqlite.Cursor: An asynchronous cursor object for SQL operations.
        """
        async with self.pool as pool:
            async with pool.acquire() as conn:
                conn.row_factory = sqlite3.Row  # type: ignore
                async with conn.cursor() as cursor:
                    yield cursor

    async def create_tables(self) -> None:
        """
        Create database tables by executing all `.sql` files in the schema directory.

        Raises:
            Exception: If any SQL file fails during execution.
        """
        async with self.get_cursor() as cursor:
            for file in os.listdir(path=self.db_scheme_basepath):
                if file.endswith(".sql"):
                    with open(f"{self.db_scheme_basepath}/{file}", "r") as f:
                        try:
                            await cursor.execute(f.read())
                        except Exception as e:
                            raise Exception("Failed to create a table") from e

    async def check_if_problem_exists(self, problem_id: str) -> bool:
        """
        Check whether a specific problem ID exists in the cache.

        Args:
            problem_id (int): The problem ID to verify.

        Returns:
            bool: True if the problem exists, False otherwise.
        """
        return await self.problem_cache.exists(problem_id)

    async def insert_checkmk_problem(
        self, checkmk_payload: ServiceNotification | HostNotification
    ) -> int | None:
        async with self.get_cursor() as cursor:
            try:
                # Insert Checkmk problem and return the inserted ID
                if isinstance(checkmk_payload, ServiceNotification):
                    cmkp = checkmk_payload
                    await cursor.execute(
                        """
                        INSERT INTO t_checkmk_problems (host_name, service_check_command, service_description, problem_id, type, state, raw_payload)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT(problem_id) DO UPDATE SET
                            state = excluded.state,
                            updated_at = datetime('now')
                        RETURNING id
                        """,
                        (
                            cmkp.host_name,
                            cmkp.service_check_command,
                            cmkp.service_desc,
                            cmkp.service_problem_id,
                            "service",
                            cmkp.service_state,
                            cmkp.model_dump_json(),
                        ),
                    )
                    row = await cursor.fetchone()
                elif isinstance(checkmk_payload, HostNotification):
                    cmkp = checkmk_payload
                    await cursor.execute(
                        """
                        INSERT INTO t_checkmk_problems (host_name, problem_id, type, state, raw_payload)
                        VALUES (?, ?, ?, ?, ?)
                        ON CONFLICT(problem_id) DO UPDATE SET
                            state = excluded.state,
                            updated_at = datetime('now')
                        RETURNING id
                        """,
                        (
                            cmkp.host_name,
                            cmkp.host_problem_id,
                            "host",
                            cmkp.host_state,
                            cmkp.model_dump_json(),
                        ),
                    )

                    row = await cursor.fetchone()
                return row[0] if row else None
            except Exception as e:
                self.logger.error(
                    "Failed to insert problem id into database.", stack_info=True
                )
                print(e)
                raise CheckmkDBInsertionError()

    async def insert_request(self, request_id: int, status: str) -> int | None:
        async with self.get_cursor() as cursor:
            try:
                await cursor.execute(
                    """
                    INSERT INTO t_servicedesk_requests (request_id, status) 
                    VALUES (?, ?)
                    ON CONFLICT(request_id) DO UPDATE SET
                        status = excluded.status,
                        updated_at = datetime('now')
                    RETURNING id
                    """,
                    (request_id, status),
                )
                row = await cursor.fetchone()
                return row[0] if row else None
            except Exception as e:
                self.logger.error(
                    f"Failed to insert request id into database: {e}", stack_info=True
                )

    async def link_problem_and_request(self, alert_id: int, request_id: int) -> None:
        async with self.get_cursor() as cursor:
            try:
                await cursor.execute(
                    """
                    INSERT INTO t_problem_request_links (alert_id, request_id)
                    VALUES (?, ?)
                    """,
                    (alert_id, request_id),
                )
            except Exception:
                self.logger.exception(
                    "Failed to insert the link between the problem and request into the database.",
                    stack_info=True,
                )

    async def check_if_request_exists(self, alert_id: int) -> int | None:
        async with self.get_cursor() as cursor:
            try:
                await cursor.execute(
                    """
                    SELECT request_id
                    FROM t_problem_request_links
                    WHERE alert_id = ?
                    """,
                    (alert_id),
                )
                row = await cursor.fetchone()
                if row:
                    return row[0]
                return None
            except Exception:
                self.logger.exception(
                    f"Failed to check if a request exists in the database. {alert_id}",
                    stack_info=True,
                )

    async def get_checkmk_info(self, request_id: int) -> None | CheckmkInfo:
        async with self.get_cursor() as cursor:
            try:
                await cursor.execute(
                    """
                    SELECT 
                        p.id,
                        p.host_name,
                        p.service_check_command,
                        p.service_description,
                        p.acknowledged,
                        p.state,
                        p.type
                    FROM t_servicedesk_requests r
                    JOIN t_problem_request_links l ON r.id = l.request_id
                    JOIN t_checkmk_problems p ON l.alert_id = p.id
                    WHERE r.request_id = ?;
                    """,
                    (request_id),
                )
                row = await cursor.fetchone()
                if row:
                    return CheckmkInfo.from_sqlite_row(row)
                return None
            except Exception:
                raise

    async def update_checkmk_acknowledged(self, id: int) -> bool:
        async with self.get_cursor() as cursor:
            try:
                await cursor.execute(
                    """
                    UPDATE t_checkmk_problems
                    SET acknowledged = 1,
                        updated_at = datetime('now')
                    WHERE id = ?
                    """,
                    (id,),
                )
            except Exception as e:
                raise e
            else:
                return True


class ProblemCache:
    def __init__(self, logger: Logger) -> None:
        """
        Initialize a ProblemCache instance.

        Args:
            logger (Logger): Logger instance for debug messages.
        """
        self.cache = []
        self.logger = logger

    async def refresh_cache(self, db: DB) -> None:
        """
        Refresh the problem cache by fetching problem IDs from the database.

        Args:
            db (DB): An instance of the DB class providing a method to obtain cursors.

        Side Effects:
            Updates the internal cache with a set of problem IDs.
            Logs a debug message upon successful refresh.
        """
        self.logger.debug(f"Old problem_cache: {self.cache}")
        async with db.get_cursor() as cursor:
            await cursor.execute(
                """
                SELECT 
                    l.alert_id, 
                    r.request_id AS servicedesk_request_id,
                    p.state AS checkmk_state,
                    p.type as checkmk_type,
                    p.problem_id as problem_id,
                    r.status AS request_state
                FROM t_problem_request_links l
                JOIN t_checkmk_problems p ON l.alert_id = p.id
                JOIN t_servicedesk_requests r ON l.request_id = r.id
            """
            )
            rows = await cursor.fetchall()
            self.cache = [CombinedRequest.from_sqlite_row(row) for row in rows]
            self.logger.debug("Refreshed problem cache...")
            self.logger.debug(f"Updated problem_cache: {self.cache}")

    async def exists(self, key) -> bool:
        """
        Check if a given key exists in the problem cache.

        Args:
            key (int): The problem ID to check.

        Returns:
            bool: True if key exists in the cache, False otherwise.
        """
        ids = [str(request.checkmk_problem_id) for request in self.cache]
        return key in ids
