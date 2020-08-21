#!/bin/env python3

import pytest
import os
from src.get_db_stats import lambdaHandler

events = {}
context = {}

def test_get_db_stats():
    results = lambdaHandler(events, context)
    assert results
