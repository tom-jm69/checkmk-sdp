#!/usr/bin/env python3
# Copyright (C) 2025-present Tom Müller - License: GNU General Public License v3
# This file is part of the Checkmk-sdp API client. It is subject to the terms and
# conditions defined in the file LICENSE or at <https://www.gnu.org/licenses/>.

import logging
import logging.config
import os

from src.conf import LOG_LEVEL, LOG_PATH

if not os.path.exists(LOG_PATH):
    os.mkdir(LOG_PATH)


class ColorFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": "\033[94m",  # Blue
        "INFO": "\033[0;32m",  # Green
        "WARNING": "\033[93m",  # Yellow
        "ERROR": "\033[91m",  # Red
        "CRITICAL": "\033[1;31m",  # Bold Red
        "RESET": "\033[0m",  # Reset to default
    }

    def format(self, record):
        color = self.COLORS.get(record.levelname, self.COLORS["RESET"])
        reset = self.COLORS["RESET"]
        original_format = self._style._fmt
        self._style._fmt = f"{color}{original_format}{reset}"
        formatted = super().format(record)
        self._style._fmt = original_format  # Reset format to avoid side effects
        return formatted


def setup_logger(name: str) -> logging.Logger:
    logging.config.dictConfig(LOG_CONFIG)

    root_logger = logging.getLogger()

    for handler in root_logger.handlers:
        # Apply color only to console (StreamHandler, not FileHandler)
        if isinstance(handler, logging.StreamHandler) and not isinstance(
            handler, logging.FileHandler
        ):
            handler.setFormatter(
                ColorFormatter(
                    "[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s",
                    "%Y-%m-%d %H:%M:%S",
                )
            )

    return logging.getLogger(name)


LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {  # For console with colors (set programmatically)
            "format": "[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "file": {  # Plain formatter for file logs
            "format": "[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "formatter": "default",  # Will be overridden with color formatter in code
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": f"{LOG_PATH}/app-{logging.getLevelName(LOG_LEVEL)}.log",
            "mode": "a",  # Append mode
            "formatter": "file",
        },
    },
    "root": {
        "handlers": ["console", "file"],
        "level": LOG_LEVEL,
    },
}
