#!/bin/env python3

import logging
import os
from typing import Dict, List, Union, Any

log_level = os.environ.get('LOG_LEVEL', logging.DEBUG)
logging.basicConfig(format='%(levelname)s:%(module)s/%(filename)s.%(funcName)s:%(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(log_level)

# typing
JSONType = Union[
    Dict[str, Any],
    List[Dict[str, Any]]
]
