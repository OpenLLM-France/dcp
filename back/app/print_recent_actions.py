#!/usr/bin/env python3

import sys
import json
import time

from datetime import datetime, timezone, timedelta

from service import DataCollectionPlatform
from database import get_db


def pretty_format_tag(label, action):
    if action:
        return '+' + label
    else:
        return '-' + label


def main():
    srv = DataCollectionPlatform()
    db = next(get_db())
    last_vote_ts = (datetime.now(timezone.utc) - timedelta(days=1)).replace(tzinfo=None)
    last_tag_ts = (datetime.now(timezone.utc) - timedelta(days=1)).replace(tzinfo=None)
    last_known_vote = 0
    last_known_tag = 0

    hdr = '     Timestamp |     Id |  UId | Task instance Id                     |' \
          ' Prompt Id                            | Generation Id                        | Vote | Tag '
    print(hdr)

    while True:
        lst = srv.get_votes_since(db, last_vote_ts, last_known_vote) \
            + srv.get_tags_since(db, last_tag_ts, last_known_tag)
        lst.sort(key=lambda item: item['timestamp'])

        for item in lst:
            fields = [
                str(item['timestamp'].strftime('%m-%d %H:%M:%S')),
                f'{item["id"]:>6}',
                f'{item["user_id"]:>4}',
                str(item['taskinstance_id']),
                str(item['prompt_id']),
                str(item['generation_id']) if 'generation_id' in item else ' ' * 36,
                f'{item["answer"]:>4}' if item['type'] in [ 'vote' ] else '    ',
                pretty_format_tag(item['label'], item['set']) if item['type'] in [ 'tag' ] else ''
            ]
            print(' | '.join(fields))

            if 'vote' == item['type']:
                last_vote_ts = item['timestamp']
                last_known_vote = max(last_known_vote, item['id'])
            elif 'tag' == item['type']:
                last_tag_ts = item['timestamp']
                last_known_tag = max(last_known_tag, item['id'])
        #break

        time.sleep(1)


if __name__ == '__main__':
    sys.exit(main())
