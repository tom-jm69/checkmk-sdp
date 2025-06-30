#!/usr/bin/env python3
# Copyright (C) 2025-present Tom Müller - License: GNU General Public License v3
# This file is part of the Checkmk-sdp API client. It is subject to the terms and
# conditions defined in the file LICENSE or at <https://www.gnu.org/licenses/>.

import bcrypt
from fastapi import Header, HTTPException, status

import src.conf as conf

if not conf.TOKEN_HASH:
    raise RuntimeError("TOKEN_HASH is missing in the environment.")


async def verify_token(authorization: str = Header(...)):
    """Verify Bearer Auth Token"""
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format. Use Bearer <token>.",
        )

    token = authorization.removeprefix("Bearer ").strip().encode("utf-8")
    if not bcrypt.checkpw(token, conf.TOKEN_HASH):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing token.",
        )
