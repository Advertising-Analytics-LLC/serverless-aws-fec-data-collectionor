#!/bin/env python3
"""
Functions for serialization
"""
import datetime
from typing import Any

def serialize_dates(o: Any) -> str:
    """Helper function to serialize datetimes
    thnx https://stackoverflow.com/a/11875813/5568528
    """
    if isinstance(o, (datetime.date, datetime.datetime)):
        return o.isoformat()
