#!/bin/env python3
"""RSSSubscriber
- Polls FEC RSS feed for new filings
    - https://efilingapps.fec.gov/rss/display?input
    - F3/F3P/F3X RSS feeds
- Sends committee_id to SNS
"""

import boto3
import json
import os
import re
import requests
from bs4 import BeautifulSoup
from requests import Response
from src import logger
from src.backfill import get_next_day
from src.database import Database
from src.OpenFec import OpenFec
from src.secrets import get_param_value_by_name
from src.sns import send_message_to_sns
from typing import Any, Dict, List


class EFilingRSSFeed:
    """wrapper for the FEC Electronic Filing RSS Feed
    https://efilingapps.fec.gov/rss/display?input
    """

    def __init__(self):
        """returns self with the basic info we need to start pulling at the RSS feed
        """
        self.base_url = 'https://efilingapps.fec.gov/rss/generate'
        self.query_param = '?preDefinedFilingType='
        self.filings_of_interest = {
            'presidential': 'F3P',
            'congressional': 'F3',
            'pac_and_party': 'F3X'
        }

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
        """takes in requests.Response, gets xml, parses xml, returns committee_id

        Args:
            rss (str): XML RSS from requests.Response.content - baiscally a big list of

        <title>New filing by LOCAL 32BJ SERVICE EMPLOYEES INTERNATIONAL UNION AMERICAN DREAM POLITICAL ACTION FUND</title>
        <link/>http://docquery.fec.gov/dcdev/posted/1418494.fec
        <description>&lt;p&gt;The CBOE GLOBAL MARKETS, INC. PAC (CBOE PAC) successfully filed  their F3XN JULY MONTHLY with the coverage period of
        06/01/2020 to 06/30/2020 and a confirmation ID of FEC-1418518&lt;/p&gt;*********
        CommitteeId: C00100693 | FilingId: 1418518 | FormType: F3XN | CoverageFrom: 06/01/2020 | CoverageThrough: 06/30/2020 | ReportType: JULY MONTHLY
        *********</description<pubdate>Fri, 10 Jul 2020 11:15:40 GMT</pubdate>
        <guid>http://docquery.fec.gov/dcdev/posted/1418495.fec</guid>
        <dc:date>2020-07-10T11:15:40Z</dc:date>
        </item>
        <item>>

        Returns:
            List[dict]: The RSS items as a list of dictionaries
        """

        # gets committee_id and
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
            # logger.debug(help(desc))
            id_list.append({
                'committee_id': parse_for_x('(CommitteeId: )([C]?[0-9]*)', desc),
                'filing_id': parse_for_x('(FilingId: )([0-9]*)', desc),
                'form_type':  parse_for_x('(FormType: )([F3XNP]*)', desc),
                'guid': desc.guid.text if desc.guid else desc.link
            })
        logger.debug(id_list)

        return id_list

    def get_items_from_rss_feeds_of_interest(self) -> List[str]:
        """gets committee_ids from all endpoints of interest

        Returns:
            List[str]: list of committee_ids
        """

        items = []
        for key, item in self.filings_of_interest.items():
            rss = self.get_rss_by_type(item)
            rss_items = self.parse_rss(rss)
            items += rss_items

        return items


# handler for aws lambda
def lambdaHandler(event: dict, context: object):
    """lambdaHandler

    Args:
        event (dict): json object containing headers and body of request
        context (bootstrap.LambdaContext): see https://docs.aws.amazon.com/lambda/latest/dg/python-context.html
    """

    eFilingRSSFeed = EFilingRSSFeed()
    items = eFilingRSSFeed.get_items_from_rss_feeds_of_interest()
    sns_replies = []

    for item in items:
        ret = send_message_to_sns(item)
        sns_replies.append(ret)

    return sns_replies


def get_filings_last_date() -> str:
    """ gets date of last filing from db """

    query = 'select min(receipt_date) from fec.filings;'
    with Database() as db:
        query_result = db.query(query)
        last_date = query_result[0][0]
        return last_date


def sync_filings_on(min_receipt_date: str) -> List[Dict[str, Any]]:
    """ retrieves all the filings recieved on a given date """

    API_KEY = get_param_value_by_name(os.environ['API_KEY'])

    max_receipt_date = get_next_day(min_receipt_date)
    get_filings_payload = {
        'min_receipt_date': min_receipt_date,
        'max_receipt_date': max_receipt_date}

    openFec = OpenFec(API_KEY)
    response_generator = openFec.get_route_paginator(
                                '/filings/',
                                get_filings_payload)

    replies = []
    for response in response_generator:
        results = response['results']
        for result in results:
            msg = {
                'committee_id': str(result['committee_id']),
                'filing_id': str(result['fec_file_id']),
                'form_type':  str(result['form_type']),
                'guid': str(result['fec_url'])
            }
            replies.append(send_message_to_sns(msg))

    return replies


def lambdaBackfillHandler(event: dict, context: object):
    """lambdaBackfillHandler

    Args:
        event (dict): json object containing headers and body of request
        context (bootstrap.LambdaContext): see https://docs.aws.amazon.com/lambda/latest/dg/python-context.html
    """
    from src.backfill import get_previous_day

    sns_replies = []
    last_date = get_filings_last_date()
    next_date = get_previous_day(last_date)

    sns_replies = sync_filings_on(next_date)

    return sns_replies
