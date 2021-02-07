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

    event_barrier: str = None
    for item in map_prefix_to_barrier:
        if event_prefix.startswith(item):
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
        objects = list(bucket.objects.filter(Prefix=prefix))
        print(f'prefix {prefix} has {len(objects)} objects')

        for i in range(0, len(objects)):
            print(f'prefix {prefix} key {objects[i].key}')

        if len(objects) is 0 or objects[i].key == prefix + '/':
            missing = True

    if missing:
        print(f'condition not met for event barrier {event_barrier}')
    else:
        print(f'condition is  met for event barrier {event_barrier}')


if __name__ == '__main__':
    with open('tests/eventbarrier_test.json') as f:
        event: dict = json.load(f)

    lambda_handler(event, "stub")
