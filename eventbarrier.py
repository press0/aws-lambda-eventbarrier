import json
import os
from typing import Dict, List

import boto3

s3_client = boto3.client('s3')


def set_s3_client(mock_s3_client: object):
    global s3_client
    s3_client = mock_s3_client


def s3_head(s3bucket_nm: str, object_key: str):
    try:
        s3_client.head_object(Bucket=s3bucket_nm, Key=object_key)
    except Exception as e:
        print(f'Object: {object_key} was not found in {s3bucket_nm} S3 bucket.:\n {e}')
        return False
    else:
        print(f'Object: {object_key} was found in {s3bucket_nm} S3 bucket.')
        return True


def lambda_handler(event, context):
    bucket_name = 'eventbarrier'

    print('## ENVIRONMENT VARIABLES')
    # print(os.environ)
    print('## EVENT')
    print(event, context)
    event_key = event['Records'][0]['s3']['object']['key']
    event_prefix = event_key[:event_key.rfind('/')]

    with open('eventbarrier.json') as f:
        map_barrier_to_prefixes: dict = json.load(f)

    map_prefix_to_barrier: Dict[str, List[str]] = {}
    for item in map_barrier_to_prefixes:
        for value in list(map_barrier_to_prefixes[item]):
            if value in map_prefix_to_barrier:
                map_prefix_to_barrier[value].append(item)
            else:
                map_prefix_to_barrier[value] = list([item])

    event_barrier: str = None
    for item in map_prefix_to_barrier:
        if item.startswith(event_prefix):
            event_barrier = map_prefix_to_barrier[item][0]
            break

    print(f'map_barrier_to_prefixes {map_barrier_to_prefixes}')
    print(f'map_prefix_to_barrier {map_prefix_to_barrier}')
    print(f'new_event {event_key}')

    if event_barrier is None:
        print(f'event {event_key} is not associated with an event barrier')
        return
    else:
        print(f'event {event_key} is associated with event barrier {event_barrier} ')

    print(f'determine if event barrier {event_barrier} condition is met')

    missing: bool = False
    for prefix in list(map_barrier_to_prefixes[event_barrier]):

        # make object_key from prefix and event
        object_key = prefix + "/file1.txt"

        if not s3_head(bucket_name, object_key):
            missing = True

    if missing:
        print(f'condition not met for event barrier {event_barrier}')
        return False
    else:
        print(f'condition is  met for event barrier {event_barrier}')
        return True


if __name__ == '__main__':
    with open('zzzz/eventbarrier_test.json') as f:
        event: dict = json.load(f)

    lambda_handler(event, "stub")
