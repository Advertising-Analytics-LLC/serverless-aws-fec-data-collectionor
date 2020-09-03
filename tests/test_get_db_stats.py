#!/bin/env python3
"""
tests src/get_db_stats.py
"""

import pytest
import os
from src.get_db_stats import lambdaHandler


events = {}
context = {}

def test_get_db_stats():
    results = lambdaHandler(events, context)
    assert results
