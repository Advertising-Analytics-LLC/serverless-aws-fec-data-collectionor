import datetime
import json
import openfec_sdk
from openfec_sdk import Configuration
import os
from src.secrets import get_param_value_by_name
from src.cerealization import serialize_dates


API_KEY = get_param_value_by_name('/dev/openfec-api/api_key')

def hello(event, context):
    """ Call the Dates (/election-dates) API and pull the most recent general election as a test.

    Args:
        event (dict): json object containing headers and body of request
        context (bootstrap.LambdaContext): see https://docs.aws.amazon.com/lambda/latest/dg/python-context.html

    Returns:
        json: most recent general election
    """
    per_page = 1
    sort = '-election_date'

    configuration = openfec_sdk.Configuration()
    api_instance = openfec_sdk.DatesApi(openfec_sdk.ApiClient(configuration))

    api_response = api_instance.election_dates_get(
        API_KEY,
        per_page=per_page,
        sort=sort)

    response_dict = api_response.to_dict()
    latest_election = response_dict['results'][0]
    body = latest_election

    response = {
        'statusCode': 200,
        'body': json.dumps(body, default=serialize_dates)
    }

    return response
