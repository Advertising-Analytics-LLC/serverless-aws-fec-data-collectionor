#!/bin/env python3

import datetime
import logging
import os
from typing import Dict, List, Union, Any


log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
logger = logging.getLogger(__name__)
logger.setLevel(log_level)

# typing
JSONType = Union[
    Dict[str, Any],
    List[Dict[str, Any]]
]

def serialize_dates(o: Any) -> str:
    """Helper function to serialize datetimes
    thnx https://stackoverflow.com/a/11875813/5568528
    """
    if isinstance(o, (datetime.date, datetime.datetime)):
        return o.strftime('%Y-%m-%d')
