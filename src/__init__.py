#!/bin/env python3

import logging
import os

log_level = os.environ.get('LOG_LEVEL', logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(log_level)
