#!/bin/env python3
""" FEC data pulling library
this file contains logging and utils
"""

import logging
import os
from datetime import date, datetime
from typing import Dict, List, Union, Any


log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
logger = logging.getLogger(__name__)
logger.setLevel(log_level)

# typing
JSONType = Union[
    Dict[str, Any],
    List[Dict[str, Any]]
]


def condense_dimension(containing_dict: Dict[str, Any], column_name: str) -> Dict[str, Any]:
    """takes a dimension (list) in a dictionary and joins the elements with ~s
        WARNING: this method uses dict.pop and so has side effets

    Args:
        containing_dict (Dict[str, Any]): Dictionary containing the
        column_name (str): to join

    Returns:
        Dict[str, Any]: input dict with that list as a str
    """

    if containing_dict.get(column_name, None) is not None:
        containing_dict[column_name] = '~'.join([str(item) for item in containing_dict.pop(column_name)])

    return containing_dict


def get_current_cycle_year() -> str:
    """  The cycle begins with an odd year and is named for its ending, even year """
    current_year = datetime.today().strftime('%Y')
    is_even_year = int(current_year) % 2 == 0
    if is_even_year:
        return current_year
    return str(int(current_year) + 1)

def serialize_dates(o: Any) -> str:
    """Helper function to serialize datetimes
    thnx https://stackoverflow.com/a/11875813/5568528
    """
    if isinstance(o, (date, datetime)):
        return o.strftime('%Y-%m-%d')
    return o
