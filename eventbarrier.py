import json
import os
from typing import Dict, List

import boto3


def lambda_handler(event, context):
    bucket_name = 'eventbarrier'
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)

    print('## ENVIRONMENT VARIABLES')
    print(os.environ)
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

    barrier: str = None
    for item in map_prefix_to_barrier:
        if event_prefix.startswith(item):
            barrier = map_prefix_to_barrier[item][0]
            break

    print(f'map_barrier_to_prefixes {map_barrier_to_prefixes}')
    print(f'map_prefix_to_barrier {map_prefix_to_barrier}')
    print(f'new_event {event_key}')

    if barrier is None:
        print(f'event {event_key} is not associated with any barrier')
        return
    else:
        print(f'event {event_key} is associated with barrier {barrier} ')

    print(f'determine if barrier {barrier} condition is met')

    missing: bool = False
    for prefix in list(map_barrier_to_prefixes[barrier]):
        objects = list(bucket.objects.filter(Prefix=prefix))
        print(f'prefix {prefix} has {len(objects)} objects')

        for i in range(0, len(objects)):
            print(f'prefix {prefix} key {objects[i].key}')

        if len(objects) is 0 or objects[i].key == prefix + '/':
            missing = True

    if missing:
        print(f'barrier condition not met for {barrier}')
    else:
        print(f'barrier condition is  met for {barrier}')


if __name__ == '__main__':
    with open('eventbarrier_test.json') as f:
        event: dict = json.load(f)

    lambda_handler(event, "stub")
