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
from typing import List, Dict


# SSM VARS
RSS_SNS_TOPIC_ARN = os.getenv('RSS_SNS_TOPIC_ARN')

client = boto3.client('sns')

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


def send_message_to_sns(msg: str) -> Dict[str, str]:
    """sends a single message to sns

    Args:
        msg (str): message
    """

    logger.debug(f'sending {msg} to sns')

    sns_response = client.publish(
        TopicArn=RSS_SNS_TOPIC_ARN,
        Message=str(msg))

    return sns_response


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
