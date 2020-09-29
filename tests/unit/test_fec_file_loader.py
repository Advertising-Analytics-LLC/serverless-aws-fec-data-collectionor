#!/bin/env python3
"""
tests
"""

import pytest
from src import FECFileLoader
from unittest.mock import patch
from moto import mock_s3


@pytest.fixture
def eventrecord():
    return {'body': "{\n  \"Type\" : \"Notification\",\n  \"MessageId\" : \"50ed91ca-725b-5192-9045-c61d7ccef752\",\n  \"TopicArn\" : \"arn:aws:sns:us-east-1:648881544937:fec-datasync-resources-RSSFeedTopic-176ER9B6NM31K\",\n  \"Message\" : \"{'committee_id': 'C00128975', 'filing_id': 'FEC-1388782', 'form_type': 'F3X', 'guid': 'http://docquery.fec.gov/paper/posted/1388782.fec'}\",\n  \"Timestamp\" : \"2020-09-12T17:58:45.903Z\",\n  \"SignatureVersion\" : \"1\",\n  \"Signature\" : \"bHEkW5HF+peedBQvL6qPxTuQTaVk1q2Lc5srS4VP6FVRRpxHoSPxAvRtRYCDh1M6ZTZi5habEub3X7dBsd5oeEl7paAs5rfAJKWbKVUk+SelaugI4bpwdQdoJ3mJxo359cPiwtyKjkRtIcLKldgskgZP2srxyZq9kdjyFyv1g01oQn4WJ7CffU2evinGKwX9qAN69S0vJmOskGwGx7XeZbFDQ07/+5LeYvTzCZvcb4YITf1TXFzsLJDnRVTdq9wixl3M+qiX7jJoYTpPF+Gp9sz6MnjS6WtOZgbDfW+V9+U7+DwAy1sY3I+OpSeSCA4TLRCL2VudiYGAlgaWWrVzvg==\",\n  \"SigningCertURL\" : \"https://sns.us-east-1.amazonaws.com/SimpleNotificationService-a86cb10b4e1f29c941702d737128f7b6.pem\",\n  \"UnsubscribeURL\" : \"https://sns.us-east-1.amazonaws.com/?Action=Unsubscribe&SubscriptionArn=arn:aws:sns:us-east-1:648881544937:fec-datasync-resources-RSSFeedTopic-176ER9B6NM31K:0d13a424-1e27-4de4-b859-d2117b15dd25\"\n}" }

@pytest.fixture
def badeventrecord():
    return {'body': "{\n  \"Type\" : \"Notification\",\n  \"MessageId\" : \"50ed91ca-725b-5192-9045-c61d7ccef752\",\n  \"TopicArn\" : \"arn:aws:sns:us-east-1:648881544937:fec-datasync-resources-RSSFeedTopic-176ER9B6NM31K\",\n  \"Message\" : \"{'committee_id': 'C00128975', 'filing_id': 'None', 'form_type': 'F3X', 'guid': 'http://docquery.fec.gov/paper/posted/1388782.fec'}\",\n  \"Timestamp\" : \"2020-09-12T17:58:45.903Z\",\n  \"SignatureVersion\" : \"1\",\n  \"Signature\" : \"bHEkW5HF+peedBQvL6qPxTuQTaVk1q2Lc5srS4VP6FVRRpxHoSPxAvRtRYCDh1M6ZTZi5habEub3X7dBsd5oeEl7paAs5rfAJKWbKVUk+SelaugI4bpwdQdoJ3mJxo359cPiwtyKjkRtIcLKldgskgZP2srxyZq9kdjyFyv1g01oQn4WJ7CffU2evinGKwX9qAN69S0vJmOskGwGx7XeZbFDQ07/+5LeYvTzCZvcb4YITf1TXFzsLJDnRVTdq9wixl3M+qiX7jJoYTpPF+Gp9sz6MnjS6WtOZgbDfW+V9+U7+DwAy1sY3I+OpSeSCA4TLRCL2VudiYGAlgaWWrVzvg==\",\n  \"SigningCertURL\" : \"https://sns.us-east-1.amazonaws.com/SimpleNotificationService-a86cb10b4e1f29c941702d737128f7b6.pem\",\n  \"UnsubscribeURL\" : \"https://sns.us-east-1.amazonaws.com/?Action=Unsubscribe&SubscriptionArn=arn:aws:sns:us-east-1:648881544937:fec-datasync-resources-RSSFeedTopic-176ER9B6NM31K:0d13a424-1e27-4de4-b859-d2117b15dd25\"\n}" }

def test_parse_good_event(eventrecord):
    parsed_msg, filing_id = FECFileLoader.parse_event_record(eventrecord)
    assert parsed_msg == {'committee_id': 'C00128975', 'filing_id': 'FEC-1388782', 'form_type': 'F3X', 'guid': 'http://docquery.fec.gov/paper/posted/1388782.fec'}
    assert filing_id == 1388782

def test_parse_bad_event(badeventrecord):
    with pytest.raises(Exception) as excinfo:
        parsed = FECFileLoader.parse_event_record(badeventrecord)
    assert 'Missing filing ID for filing record ' in str(excinfo.value)

# @mock_s3
# def test_write_and_load():
#     pass
