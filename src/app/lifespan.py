#!/usr/bin/env python3
# Copyright (C) 2025-present Tom Müller - License: GNU General Public License v3
# This file is part of the Checkmk-sdp API client. It is subject to the terms and
# conditions defined in the file LICENSE or at <https://www.gnu.org/licenses/>.

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

import src.conf as conf

from .checkmk.client import Checkmk
from .coordinator.client import LogicCoordinator
from .database.client import DB
from .sdp.client import SDP
from .utils import setup_logger


def start_pollers(app: FastAPI):
    try:
        asyncio.create_task(app.state.sdp.start())
        asyncio.create_task(app.state.checkmk.start())
        asyncio.create_task(app.state.db.start())
        asyncio.create_task(app.state.coordinator.start())
    except Exception:
        app.state.logger.exception(
            "Error while starting background pollers", stack_info=True
        )
        raise RuntimeError("Failed to launch pollers.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.logger = setup_logger("fastapi")
    print("Log Level:", logging.getLevelName(conf.LOG_LEVEL))
    app.state.logger.level = conf.LOG_LEVEL
    startup_message = r"""
   _____ _               _              _         _______ _____  _____    _____       _                       _   _             
  / ____| |             | |            | |       / / ____|  __ \|  __ \  |_   _|     | |                     | | (_)            
 | |    | |__   ___  ___| | ___ __ ___ | | __   / / (___ | |  | | |__) |   | |  _ __ | |_ ___  __ _ _ __ __ _| |_ _  ___  _ __  
 | |    | '_ \ / _ \/ __| |/ / '_ ` _ \| |/ /  / / \___ \| |  | |  ___/    | | | '_ \| __/ _ \/ _` | '__/ _` | __| |/ _ \| '_ \ 
 | |____| | | |  __/ (__|   <| | | | | |   <  / /  ____) | |__| | |       _| |_| | | | ||  __/ (_| | | | (_| | |_| | (_) | | | |
  \_____|_| |_|\___|\___|_|\_\_| |_| |_|_|\_\/_/  |_____/|_____/|_|      |_____|_| |_|\__\___|\__, |_|  \__,_|\__|_|\___/|_| |_|
                                                                                               __/ |                            
                                                                                              |___/                             
        """
    app.state.logger.info(startup_message)
    app.state.sdp = SDP(
        url=conf.SDP_URL,
        port=conf.SDP_PORT,
        scheme=conf.SDP_SCHEME,
        secret=conf.SDP_SECRET,
        requester_name=conf.SDP_REQUESTER_NAME,
        requester_id=conf.SDP_REQUESTER_ID,
        verify_ssl=conf.SDP_VERIFY_SSL,
        timeout=conf.SDP_TIMEOUT,
        api_version=conf.SDP_API_VERSION,
    )
    app.state.checkmk = Checkmk(
        url=conf.CHECKMK_URL,
        port=conf.CHECKMK_PORT,
        scheme=conf.CHECKMK_SCHEME,
        username=conf.CHECKMK_USERNAME,
        secret=conf.CHECKMK_SECRET,
        site_name=conf.CHECKMK_SITE_NAME,
        verify_ssl=conf.CHECKMK_VERIFY_SSL,
        api_version=conf.CHECKMK_API_VERSION,
    )
    app.state.db = DB(
        db_name=conf.DB_NAME,
        db_path=conf.DB_PATH,
        db_scheme_basepath=conf.DB_SCHEME_BASEPATH,
    )
    app.state.coordinator = LogicCoordinator(
        sdp_client=app.state.sdp, checkmk_client=app.state.checkmk, db=app.state.db
    )
    try:
        start_pollers(app)
    except RuntimeError:
        app.state.logger.exception(
            "Error while trying to create background tasks", stack_info=True
        )
    else:
        app.state.logger.info("Started background tasks successfully")
    yield

    # App runs while this context is alive
    # Everything after yield will run on shutdown

    shutdown_message = "Shutting down services..."
    app.state.logger.info(shutdown_message)
    try:
        await app.state.sdp.session.close()
    except Exception:
        app.state.logger.warning("Could not close SDP client session", exc_info=True)
    try:
        await app.state.checkmk.session.close()
    except Exception:
        app.state.logger.warning(
            "Could not close Checkmk client session", exc_info=True
        )
