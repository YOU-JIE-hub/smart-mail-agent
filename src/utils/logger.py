#!/usr/bin/env python3
import logging
import sys

logger = logging.getLogger("SMA")
if not logger.handlers:
    logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.INFO)
