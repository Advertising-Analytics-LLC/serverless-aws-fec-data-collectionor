#!/bin/env python3
"""
Functions for getting secrets
"""

import boto3
from typing import List, Dict, Union, Any


JSONType = Union[str, int, float, bool, None, Dict[str, Any], List[Any]]


session = boto3.Session()
client = session.client('ssm')

def get_parameter_by_name(parameter_name: str) -> dict:
    """Gets parameters value and other attributes from AWS"""
    parameter_object = client.get_parameter(
        Name=parameter_name,
        WithDecryption=True)
    parameter = parameter_object['Parameter']
    return parameter

def get_param_value_by_name(parameter_name: str) -> str:
    """Gets SSM parameter value, decrypted

    Args:
        parameter_name (str): Name (including path) of SSM param

    Returns:
        str: The SSM param value
    """
    param = get_parameter_by_name(parameter_name)
    param_value = param['Value']
    return param_value
