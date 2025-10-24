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
    parser.add_argument('-t', '--task-id', type=str, help='Task id')
    parser.add_argument('-u', '--user-id', type=str, help='User id')
    args = parser.parse_args()

    db = next(get_db())
    srv = DataCollectionPlatform()

    if args.user_id is not None and args.task_id is None:
        res = srv.get_tasks_done_for_user(db, args.user_id)
        for row in res:
            print(f"Task ID: {row['task_id']}, Task Instance Count: {row['count']}")
    elif args.user_id is None and args.task_id is not None:
        res = srv.get_tasks_done(db, args.task_id)
        for row in res:
            print(f"User ID: {row['user_id']}, Task Instance Count: {row['count']}")
    elif args.user_id is not None and args.task_id is not None:
        res = srv.get_tasks_done_for_user_and_task(db, args.user_id, args.task_id)
        for row in res:
            print(f"Count: {row['count']}")
    else:
        res = srv.get_stat_user_task(db)

        for row in res:
            print(f"User ID: {row['user_id']}, Task ID: {row['task_id']}, Task Instance Count: {row['count']}")

    return 0


if __name__ == '__main__':
    sys.exit(main())

