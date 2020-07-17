#!/bin/env python3

import pytest
import requests
from src.RSSSubscriber import EFilingRSSFeed
from unittest.mock import MagicMock, patch
from unittest import TestCase


def get_xml_str(*args, **kwargs):
    """Mock xml"""
    with open('tests/data/2020-07-17-F3p.txt', 'r') as fh:
        xml_string = fh.read()
    return xml_string

xml_string = get_xml_str()


def get_mocked_EFilingRSSFeed(monkeypatch):
    """returns object that uses sample data"""
    monkeypatch.setattr(EFilingRSSFeed, 'get_rss_by_type', get_xml_str)
    eFilingRSSFeed = EFilingRSSFeed()
    return eFilingRSSFeed

def test_get_good_response(monkeypatch):
    """Make sure our mock object is returning our mock data"""
    eFilingRSSFeed = get_mocked_EFilingRSSFeed(monkeypatch)
    rss_type = 'F3'
    response = eFilingRSSFeed.get_rss_by_type(rss_type)
    assert response == xml_string
    assert response != 'xml_string'

def test_parse_works(monkeypatch):
    eFilingRSSFeed = get_mocked_EFilingRSSFeed(monkeypatch)
    rss_items = eFilingRSSFeed.parse_rss(xml_string)
    assert rss_items[0]['committee_id'] == 'C00724898'
