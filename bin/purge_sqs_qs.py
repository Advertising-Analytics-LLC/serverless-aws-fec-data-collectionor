#!/bin/env python3

import boto3
import list_qs

sqs = boto3.client('sqs')


queues = list_qs.list_qs()
q_str = '\t\n'.join(queues)
print(f'Purging queues:\n{q_str}')
nonelist = list(map(lambda x: sqs.purge_queue(QueueUrl=x), queues))
print('Queues purged')
