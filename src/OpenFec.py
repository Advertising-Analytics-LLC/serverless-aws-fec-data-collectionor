#!/bin/env python3
""" lightweight SDK for OpenFec API
influences:
- https://github.com/rhythmictech/pagerduty-to-jira-lambda/blob/master/pd2jira_function/pd2jira/app.py
- https://github.com/sblack4/lolcrawler2/blob/master/lolcrawler/riot.py
"""

import json
import requests
from requests import Response
from src import JSONType, logger
from time import sleep
from typing import Generator

class OpenFec:
    """Lightweight wrapper over the openFEC api - https://api.open.fec.gov/developers/
    """
    def __init__(self, api_key: str, base_url='https://api.open.fec.gov/v1'):
        """Create OpenFec api objects

        Args:
            api_key (str): get a key at https://api.data.gov/signup/
            base_url (str, optional): OpenFEC base url. Defaults to 'https://api.open.fec.gov/v1'.
        """
        self.api_key = api_key
        self.api_arg = '?api_key=' + api_key
        self.base_url = base_url
        self.throttle = 0.5 # seconds to wait between requests

    def _get_route(self, route: str) -> str:
        """internal method to get fully-formed route

        Args:
            route (str): route, eg "/committees/"

        Returns:
            str: fully-formed route, eg https://api.open.fec.gov/v1/committees/?api_key=<API_KEY>
        """
        url = self.base_url + route + self.api_arg
        return url

    def _over_rate_limit(self, response: Response) -> bool:
        """returns true if response has OVER_RATE_LIMIT error

        Args:
            response (Response): Response from requests library

        Returns:
            bool: is request OVER_RATE_LIMIT
        """
        if response.status_code == 429:
            logger.info(f'Over rate limit, {response.json()}')
            return True
        return False

    def _get_request(self, url: str, payload: dict, throttle_multiplier=1) -> Response:
        """light wrapper over requests.get
            Checks for OVER_RATE_LIMIT warning and throttles

        Args:
            url (str): url to get
            payload (dict): params payload
            throttle_multiplier (int): multiplier for throttling timeout

        Returns:
            Response: Reponse object
        """

        logger.debug(f'GET {url}, {payload}'.replace(self.api_key, 'API_KEY'))
        response = requests.get(url, params=payload)

        if response.status_code == 404:
            raise Exception(f'404 from {url}, response: {response}')

        logger.debug(response.json())
        if self._over_rate_limit(response):
            sleep_for_seconds = self.throttle * throttle_multiplier ** 2
            logger.info(f'Sleeping for {sleep_for_seconds} seconds')
            sleep(sleep_for_seconds)
            throttle_multiplier += 1
            response = self._get_request(url, payload, throttle_multiplier)

        return response

    def get_route(self, route:str, payload: dict) -> JSONType:
        """get response from openfec API
            https://api.open.fec.gov/developers/

        Args:
            payload (dict): request params object

        Returns:
            json: response as json object, has this structure:
                    {
                      "api_version": "1.0",
                      "pagination": {
                        "page": 1,
                        "per_page": 20,
                        "count": 0,
                        "pages": 0
                      },
                      "results": []
                    }
        """
        url = self._get_route(route)
        response = self._get_request(url, payload)
        return response.json()

    def get_route_paginator(self, route: str, payload={}) -> Generator:
        """paginator for any endpoint

        Args:
            payload (dict): request params

        Yields:
            Generator: python Generator object to iteratate over responses
        """
        first_response = self.get_route(route, payload)
        yield first_response
        num_pages = first_response['pagination']['pages']
        for page in range(2, num_pages + 1):
            payload['page'] = page
            next_page = self.get_route(route, payload)
            yield next_page

    def get_committees(self, payload: dict) -> JSONType:
        """get response from committee API
            https://api.open.fec.gov/developers/#/committee/get_committees_

        Args:
            payload (dict): request params object

        Returns:
            json: response as json object, has this structure:
                    {
                      "api_version": "1.0",
                      "pagination": {
                        "page": 1,
                        "per_page": 20,
                        "count": 0,
                        "pages": 0
                      },
                      "results": []
                    }
        """
        route = '/committees/'
        url = self._get_route(route)
        response = self._get_request(url, payload)
        return response.json()

    def get_committees_paginator(self, payload: dict) -> Generator:
        """paginator for committees endpoint

        Args:
            payload (dict): request params

        Yields:
            Generator: python Generator object to iteratate over committee responses
        """
        first_response = self.get_committees(payload)
        yield first_response
        num_pages = first_response['pagination']['pages']
        for page in range(2, num_pages + 1):
            payload['page'] = page
            next_page = self.get_committees(payload)
            yield next_page

    def get_committee_by_id(self, committee_id: str, payload: dict) -> JSONType:
        """gets committee info by committee_id
            see https://api.open.fec.gov/developers/#/committee/get_committee__committee_id__

        Args:
            committee_id (str): A unique identifier assigned to each committee or filer registered with the FEC.
                                In general committee id's begin with the letter C which is followed by eight digits.
            payload (dict): request params object

        Returns:
            json: response as json object, of type CommitteeDetailPage
        """
        committee_id_without_quotes = committee_id.replace('"', '')
        route = f'/committee/{committee_id_without_quotes}/'
        url = self._get_route(route)
        response = self._get_request(url, payload)
        return response.json()

    def get_committee_by_id_paginator(self, committee_id: str, payload={}) -> Generator:
        """paginator to get committee info by committee_id
            see https://api.open.fec.gov/developers/#/committee/get_committee__committee_id__

        Args:
            committee_id (str): A unique identifier assigned to each committee or filer registered with the FEC.
                                In general committee id's begin with the letter C which is followed by eight digits.
            payload (dict): request params object

        Yields:
            Generator: python Generator object to iteratate over get_committee_by_id
        """

        first_response = self.get_committee_by_id(committee_id, payload)
        yield first_response
        num_pages = first_response['pagination']['pages']
        for page in range(2, num_pages + 1):
            payload['page'] = page
            next_page = self.get_committees(committee_id, payload)
            yield next_page
