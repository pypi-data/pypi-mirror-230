#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import threading
from pathlib import Path

from loguru import logger

# Component version
__version__ = "4.5.0"

# Get component full version from file generated at build time
current_file_dir = Path(__file__).resolve().parent
fullversion_file = Path(current_file_dir, "fullversion.txt")
if os.path.isfile(fullversion_file):
    __fullversion__ = open(fullversion_file, "r").read().strip()
else:
    __fullversion__ = __version__

# Initialize loguru
config = {
    "handlers": [
        {
            "sink": sys.stdout,
            "format": "|<level>{level: ^7}</level>| {message}",
        },
    ],
}
logger.configure(**config)

shutil_make_archive_lock = threading.Lock()
