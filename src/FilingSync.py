#!/bin/env python3
"""RSSSubscriber
- Polls FEC RSS feed for new filings
    - https://efilingapps.fec.gov/rss/display?input
    - F3/F3P/F3X RSS feeds
- Sends committee_id to SNS
"""

import os
import re
import requests
from bs4 import BeautifulSoup
from src import logger
from src.backfill import get_previous_day, filings_sync_backfill_date, filings_backfill_success
from src.OpenFec import OpenFec
from src.secrets import get_param_value_by_name
from src.sns import send_message_to_sns
from typing import Any, Dict, List


form_types_of_interest = ['F3P','F3','F3X']


class EFilingRSSFeed:
    """wrapper for the FEC Electronic Filing RSS Feed
    https://efilingapps.fec.gov/rss/display?input
    """

    def __init__(self):
        """returns self with the basic info we need to start pulling at the RSS feed"""

        self.base_url = 'https://efilingapps.fec.gov/rss/generate'
        self.query_param = '?preDefinedFilingType='

    def get_rss_by_type(self, filing_type: str, payload={}) -> str:
        """Given a request type it will return that RSS as a string
        uses session, adapter to prevent this error:
            `RemoteDisconnected('Remote end closed connection without response`...

        Args:
            filing_type (str): (see self.filings_of_interest)
            payload (dict): request params object

        Returns:
            Response: XML string
        """

        url = self.base_url + self.query_param + filing_type
        logger.debug(f'GET {url}')
        headers = {
            'Accept': '*/*',
            'User-Agent': 'requests'
        }
        session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(max_retries=5)
        session.mount('https://', adapter)
        response = session.get(url, stream=True, timeout=5, headers=headers)
        logger.debug(f'status_code: {response.status_code}')

        return response.content

    def parse_rss(self, rss: str) -> List[dict]:
        """takes in xml, parses xml, returns committee_id"""

        def parse_for_x(regex: str, description: str):
            matches = re.findall(regex, str(desc), re.MULTILINE)
            if matches:
                return matches[0][1]
            return ''

        id_list = []
        soup = BeautifulSoup(rss)
        logger.debug(soup)
        items = soup.find_all('item')

        for desc in items:
            filing_id = parse_for_x('(FilingId: )([0-9]*)', desc)

            if not filing_id or filing_id is 'None':
                logger.warning(f'No fec file ID for record {desc}')
                continue

            new_filing_record = {
                'committee_id': parse_for_x('(CommitteeId: )([C]?[0-9]*)', desc),
                'filing_id': filing_id,
                'form_type':  parse_for_x('(FormType: )([F3XNP]*)', desc),
                'guid': desc.guid.text if desc.guid else desc.link
            }

            id_list.append(new_filing_record)

        return id_list

    def get_items_from_rss_feeds_of_interest(self) -> List[str]:
        """gets committee_ids from all endpoints of interest"""

        items = []
        for item in form_types_of_interest:
            rss = self.get_rss_by_type(item)
            rss_items = self.parse_rss(rss)
            items += rss_items

        return items


def lambdaHandler(event: dict, context: object):
    """lambdaHandler"""

    eFilingRSSFeed = EFilingRSSFeed()
    items = eFilingRSSFeed.get_items_from_rss_feeds_of_interest()
    sns_replies = []

    for item in items:
        ret = send_message_to_sns(item)
        sns_replies.append(ret)

    return sns_replies


def sync_filings_on(min_receipt_date: str, max_receipt_date: str) -> List[Dict[str, Any]]:
    """retrieves all the filings recieved on a given date"""

    API_KEY = get_param_value_by_name(os.environ['API_KEY'])

    get_filings_payload = {
        'min_receipt_date': min_receipt_date,
        'max_receipt_date': max_receipt_date,
        'form_type': form_types_of_interest}

    openFec = OpenFec(API_KEY)
    response_generator = openFec.get_route_paginator(
                                '/filings/',
                                get_filings_payload)

    replies = []
    for response in response_generator:
        results = response['results']
        try:
            for result in results:
                msg = {
                    'committee_id': str(result['committee_id']),
                    'filing_id': str(result['fec_file_id']),
                    'form_type':  str(result['form_type']),
                    'guid': str(result.get('fec_url', ''))
                }
                replies.append(send_message_to_sns(msg))
        except KeyError as keyError:
            logger.error(keyError)
        except Exception as e:
            logger.error(e)
            raise

    return replies


def lambdaBackfillHandler(event: dict, context: object):
    """lambdaBackfillHandler"""

    max_receipt_date = filings_sync_backfill_date()
    if not max_receipt_date:
        raise Exception('No date recieved from backfill table. Exiting.')
    min_receipt_date = get_previous_day(max_receipt_date)
    sns_replies = sync_filings_on(min_receipt_date, max_receipt_date)
    filings_backfill_success(max_receipt_date)

    return sns_replies
