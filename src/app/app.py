#!/usr/bin/env python3
# Copyright (C) 2025-present Tom Müller - License: GNU General Public License v3
# This file is part of the Checkmk-sdp API client. It is subject to the terms and
# conditions defined in the file LICENSE or at <https://www.gnu.org/licenses/>.

from fastapi import FastAPI

from .lifespan import lifespan
from .routes import router

app = FastAPI(lifespan=lifespan)
app.include_router(router)
