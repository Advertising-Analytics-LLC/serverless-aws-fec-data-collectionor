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
import boto3
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

    def get_rss_by_type(self, filing_type: str, payload={}) -> Response:
        """Given a request type it will return that RSS as a requests.Response
        uses session, adapter to prevent
        `RemoteDisconnected('Remote end closed connection without response`

        Args:
            filing_type (str): (see self.filings_of_interest)
            payload (dict): request params object

        Returns:
            Response: requests.Response containing RSS
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

        return response

    def parse_rss(self, filing_response: Response) -> List[str]:
        """takes in requests.Response, gets xml, parses xml, returns committee_id

        Args:
            filing_response (Response): requests.Response object

        Returns:
            List[dict]: The RSS items as a list of dictionaries
        """
        regex = r'(CommitteeId: )(C[0-9]*)'
        committee_id_list = []
        soup = BeautifulSoup(filing_response.content)
        descriptions = soup.find_all('description')
        for desc in descriptions:
            matches = re.findall(regex, str(desc), re.MULTILINE)
            if len(matches) > 0:
                match = matches[0][1]
                committee_id_list.append(match)

        return committee_id_list

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
    ret = client.publish(TopicArn=RSS_SNS_TOPIC_ARN, Message=msg)
    return ret

# handler for aws lambda
def lambdaHandler(event: dict, context: object):
    """lambdaHandler

    Args:
        event (dict): json object containing headers and body of request
        context (bootstrap.LambdaContext): see https://docs.aws.amazon.com/lambda/latest/dg/python-context.html
    """
    eFilingRSSFeed = EFilingRSSFeed()
    items = eFilingRSSFeed.get_items_from_rss_feeds_of_interest()
    logger.debug(items)
    for item in items:
        send_message_to_sns(item)
