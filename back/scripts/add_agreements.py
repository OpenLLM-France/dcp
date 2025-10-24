#!/usr/bin/env python3

import sys
import os
import argparse
import json

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'app'))

from database import get_db
from service import DataCollectionPlatform


def main():
    parser = argparse.ArgumentParser(description='Add agreements to the DB')
    parser.add_argument('-i', '--input', required=True, type=str, help='Input file name')
    args = parser.parse_args()

    db = next(get_db())
    srv = DataCollectionPlatform()

    try:
        with open(args.input, 'rt') as f:
            data = json.load(f)
            for item in data:
                srv.add_agreement(db, item['name'], item['description'], item['text'])

    except Exception as e:
        sys.stderr.write(f'ERROR: {e}\n')
        return -1

    return 0


if __name__ == '__main__':
    sys.exit(main())

