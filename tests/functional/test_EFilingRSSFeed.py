#!/bin/env python3

import pytest
from src.RSSSubscriber import EFilingRSSFeed


eFilingRSSFeed = EFilingRSSFeed()

def test_get_good_response():
    rss_type = 'F3'
    response = eFilingRSSFeed.get_rss_by_type(rss_type)
    assert response
