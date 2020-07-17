#!/bin/env python3

import pytest
from src.RSSSubscriber import EFilingRSSFeed
from unittest.mock import MagicMock
from unittest import TestCase

@pytest.fixture
def mock_test_response(monkeypatch):
    """Mock xml"""

    with open('test/data/2020-07-17-F3p.txt', 'r') as fh:
        xml_string = fh.readlines()
    monkeypatch.return_value(xml_string)


def test_get_good_response():
    """Make sure our mock object is returning our mock data"""

    with open('test/data/2020-07-17-F3p.txt', 'r') as fh:
        xml_string = fh.readlines()
    rss_type = 'F3'
    eFilingRSSFeed = EFilingRSSFeed()
    response = eFilingRSSFeed.get_rss_by_type(rss_type)
    assert response == xml_string
