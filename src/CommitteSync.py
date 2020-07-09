import datetime
import json
import openfec_sdk
from openfec_sdk import Configuration
import os
from src.secrets import get_param_value_by_name
from src.serialization import serialize_dates


API_KEY = get_param_value_by_name('/global/openfec-api/api_key')

def committeSync(event, context):
    """ Call the Dates (/election-dates) API and pull the most recent general election as a test.

    Args:
        event (dict): json object containing headers and body of request
        context (bootstrap.LambdaContext): see https://docs.aws.amazon.com/lambda/latest/dg/python-context.html

    Returns:
        json: most recent general election
    """
    configuration = openfec_sdk.Configuration()
    api_instance = openfec_sdk.CommitteeApi(openfec_sdk.ApiClient(configuration))

    api_response = api_instance.committees_get(
        API_KEY)

    response_dict = api_response.to_dict()
    latest_election = response_dict['results']
    body = latest_election

    response = {
        'statusCode': 200,
        'body': json.dumps(body, default=serialize_dates)
    }

    return response
