#!/usr/bin/env python3
# Copyright (C) 2025-present Tom Müller - License: GNU General Public License v3
# This file is part of the Checkmk-sdp API client. It is subject to the terms and
# conditions defined in the file LICENSE or at <https://www.gnu.org/licenses/>.

import sys

import uvicorn

from src.conf import FASTAPI_ADDRESS, FASTAPI_PORT
from src.app.app import app
from src.app.utils import LOG_CONFIG, setup_logger

logger = setup_logger("main")


def main():
    try:
        uvicorn.run(
            app,
            host=FASTAPI_ADDRESS,
            port=FASTAPI_PORT,
            log_config=LOG_CONFIG,
        )
    except KeyboardInterrupt:
        message = "Received an KeyboardInterrupt... Exiting"
        logger.critical(message)
        print(message)
        sys.exit(1)
    except Exception as e:
        logger.critical("An error occurred while starting the server.", exc_info=e)
        sys.exit(1)


if __name__ == "__main__":
    main()
