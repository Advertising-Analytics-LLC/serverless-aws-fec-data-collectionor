#!/bin/env python3

import logging
import os
from typing import Dict, List, Union, Any

log_level = os.environ.get('LOG_LEVEL', logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(log_level)

# typing
JSONType = Union[
    Dict[str, Any],
    List[Dict[str, Any]]
]
