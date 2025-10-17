#!/usr/bin/env python3

import logging
import sys
from datetime import datetime
from pathlib import Path


class ColoredFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": "\033[0;36m",
        "INFO": "\033[0;32m",
        "WARNING": "\033[1;33m",
        "ERROR": "\033[0;31m",
        "CRITICAL": "\033[1;31m",
    }
    RESET = "\033[0m"
    BOLD = "\033[1m"

    EMOJI = {
        "DEBUG": "🔍",
        "INFO": "📝",
        "WARNING": "⚠️ ",
        "ERROR": "❌",
        "CRITICAL": "🔥",
    }

    def format(self, record):
        if hasattr(sys.stdout, "isatty") and sys.stdout.isatty():
            levelname = record.levelname
            if levelname in self.COLORS:
                emoji = self.EMOJI.get(levelname, "")
                record.levelname = f"{self.COLORS[levelname]}{emoji} {levelname}{self.RESET}"
                record.msg = f"{self.COLORS[levelname]}{record.msg}{self.RESET}"
        return super().format(record)


def setup_logging(config):
    log_dir = Path(config["logging"]["directory"])
    log_dir.mkdir(exist_ok=True)

    log_file = log_dir / f"ci-plumber-{datetime.now().strftime('%Y-%m-%d')}.log"

    file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    console_formatter = ColoredFormatter("%(asctime)s - %(levelname)s - %(message)s")

    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(file_formatter)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)

    logger = logging.getLogger(__name__)
    logger.setLevel(getattr(logging, config["logging"]["level"]))
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
