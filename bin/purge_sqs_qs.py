#!/bin/env python3

import boto3


sqs = boto3.client('sqs')

q_name_prefixes = ['candidate-', 'fec-', 'committee-']

flatten = lambda l: [item for sublist in l for item in sublist]

queue_objects = list(map(lambda x: sqs.list_queues(QueueNamePrefix=x), q_name_prefixes))
queues_nested = list(map(lambda x: x['QueueUrls'], queue_objects))
queues = flatten(queues_nested)
q_str = '\t\n'.join(queues)
print(f'Purging queues:\n{q_str}')
map(lambda x: sqs.purge_queue(QueueUrl=x), queues)
print('Queues purged')
