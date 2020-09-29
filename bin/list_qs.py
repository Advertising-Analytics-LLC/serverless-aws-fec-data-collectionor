#!/bin/env python3

import boto3


sqs = boto3.client('sqs')

q_name_prefixes = ['candidate-', 'fec-', 'committee-']

flatten = lambda l: [item for sublist in l for item in sublist]

def paginate():
    qs = []
    marker = None
    paginator = sqs.get_paginator('list_queues')
    response_iterator = paginator.paginate(
        PaginationConfig={
            'PageSize': 10,
            'StartingToken': marker})
    for page in response_iterator:
        qs.append(page['QueueUrls'])
    return qs


def list_qs():
    queue_objects = list(map(lambda x: sqs.list_queues(QueueNamePrefix=x), q_name_prefixes))
    queues_nested = list(map(lambda x: x['QueueUrls'], queue_objects))
    queues = flatten(queues_nested)
    return queues


if __name__ == '__main__':
    queues = list_qs()
    q_st = '\n'.join(queues)
    print(q_st)
