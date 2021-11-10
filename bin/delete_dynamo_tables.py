#!/bin/python3

import boto3


dynamo = boto3.resource('dynamodb')

for table in dynamo.tables.all():
    table.delete()
