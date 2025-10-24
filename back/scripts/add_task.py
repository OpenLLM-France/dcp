#!/usr/bin/env python3

import sys
import os
import argparse
import json

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'app'))

from database import get_db
from service import DataCollectionPlatform


def main():
    parser = argparse.ArgumentParser(description='Adds new task to the DB')
    parser.add_argument('-n', '--name', required=True, type=str, help='Task name')
    parser.add_argument('-m', '--meta', required=True, type=str, help='Task metadata')
    parser.add_argument('-p', '--public', action='store_true', default=False, help='Task is public')
    parser.add_argument('-i', '--instruction-id', required=True, type=str, help='Instruction id')
    args = parser.parse_args()

    db = next(get_db())
    srv = DataCollectionPlatform()

    metadata = None
    try:
        with open(args.meta, 'rt') as f:
            metadata = f.read()
    except Exception as e:
        sys.stderr.write(f'ERROR: can\'t read {args.meta}:\n{e}\n')
        return -1

    existing_tasks = srv.get_tasks(db)
    for item in existing_tasks:
        if args.name == item.name:
            sys.stderr.write(f'ERROR: task with name "{args.name}" already exists:\n{item}\n')
            return -1

    try:
        new_task_id = srv.add_task(db, args.name, args.public, metadata, args.instruction_id)
    except Exception as e:
        sys.stderr.write(f'ERROR: can\'t insert new task:\n{e}\n')
        return -1

    print(new_task_id)
    return 0


if __name__ == '__main__':
    sys.exit(main())

