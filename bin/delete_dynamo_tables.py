#!/bin/python3

import boto3
from time import sleep

dynamo = boto3.resource('dynamodb')

for table in dynamo.tables.all():
    table.delete()
