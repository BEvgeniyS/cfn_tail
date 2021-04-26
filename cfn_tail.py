#!/usr/bin/env python3
import sys
import boto3
from time import sleep
from argparse import ArgumentParser


def get_sorted_cfn_stack_events(stack, latest_event=None, initial_events=10, continuous=False):
    events = []
    event_iterator = stack.events.all()
    if latest_event:
        for event in event_iterator:
            if event.event_id == latest_event.event_id:
                break
            events.append(event)
    else:
        for event in event_iterator:
            if len(events) > initial_events:
                break
            events.append(event)

    if len(events) > 0 : latest_event = events[0]
    return sorted(events, key=lambda r: r.timestamp), latest_event
parser = ArgumentParser()
parser.add_argument('-s', '--stack-name', dest='stack_name', required=True,
                    help="name of CFN stack", metavar="<STACK_NAME>")
parser.add_argument('-n', '--initial-events-count', dest='initial_events', required=False,
                    help="Number of initial events. Default is 0", default=0)
parser.add_argument('-c', '--no-stop-on-complete', action='store_true', dest='continuous', required=False,
                    help="Don't stop after stack has reached *_COMPLETED state", default=False)
args = parser.parse_args()

initial_events=args.initial_events
continuous=args.continuous
stack_name=args.stack_name
client = boto3.client('cloudformation')
cloudformation = boto3.resource('cloudformation')
stack = cloudformation.Stack(stack_name)
latest_event = None

print (f'Tailing {stack_name}')


while continuous or stack.stack_status.endswith('_IN_PROGRESS'):
    evts, latest_event = get_sorted_cfn_stack_events(stack, latest_event, initial_events)
    for evt in evts:
        status_reason = '' if evt.resource_status_reason is None else str(evt.resource_status_reason)
        print(f'{evt.timestamp:%Y-%m-%d %H:%M:%S%z} [{evt.logical_resource_id}] {evt.resource_status} {status_reason}')
    evts = None
    stack.load()
    sleep(3)

if not continuous:
    # Stack update failed
    if stack.stack_status.endswith('ROLLBACK_COMPLETE'):
        sys.exit(1)
    # Stack create/update succeeded
    elif stack.stack_status.endswith('_COMPLETE'):
        sys.exit(0)
    # Stack final state is unknown
    else:
        sys.exit(1)