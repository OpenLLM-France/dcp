#!/usr/bin/env python3

import sys
import os
import lzma
import argparse
import json

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'app'))

from database import get_db
from service import DataCollectionPlatform


def main():
    parser = argparse.ArgumentParser(description='Adds prompts and generations to the existing task')
    parser.add_argument('-t', '--task-id', required=True, type=str, help='Task id')
    parser.add_argument('-d', '--data', required=True, type=str, help='Data file name (.jsonl or .jsonl.xz)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Print more details')
    args = parser.parse_args()

    db = next(get_db())
    srv = DataCollectionPlatform()

    try:
        task_info = srv.get_task_by_id(db, args.task_id)
        if args.verbose:
            sys.stderr.write(f'Found task {args.task_id}\n')
    except Exception as e:
        sys.stderr.write(f'ERROR: {e}\n')

    prompts_added = 0
    params_added = 0
    generations_added = 0
    try:
        if args.data.endswith('.jsonl'):
            fh = open(args.data, 'rt')
        elif args.data.endswith('.jsonl.xz'):
            fh = lzma.open(args.data, 'rt')
        else:
            sys.stderr.write(f'ERROR: don\'t know how to open {args.data}\n')
            return -1
 
        for line in fh:
            if len(line) > 2:
                d = json.loads(line)

            prompt = srv.find_prompt(db, args.task_id, d['prompt'])
            if prompt is not None:
                prompt_id = prompt['id']
                if args.verbose:
                    sys.stderr.write(f'Prompt {prompt_id} already exists\n')
            else:
                prompt_id = srv.add_prompt(db, args.task_id, d['prompt'])
                prompts_added += 1

            for item in d['generations']:
                params = srv.find_generation_params(db, item['params'])
                if params is not None:
                    params_id = params['id']
                    if args.verbose:
                        sys.stderr.write(f'Params {params_id} already exists\n')
                else:
                    params_id = srv.add_generation_params(db, item['params'])
                    params_added += 1

                generation = srv.find_generation(db, item['text'], params_id, prompt_id)
                if generation is not None:
                    gen_id = generation['id']
                    if args.verbose:
                        sys.stderr.write(f'Generation {gen_id} already exists\n')
                else:
                    gen_id = srv.add_generation(db, item['text'], params_id, prompt_id)
                    generations_added += 1
                    if args.verbose:
                        sys.stderr.write(f'New generation id == {gen_id}\n')

        if args.verbose:
            sys.stderr.write(f'Added:\n')
            sys.stderr.write(f'\t{prompts_added} prompts\n')
            sys.stderr.write(f'\t{params_added} generation params\n')
            sys.stderr.write(f'\t{generations_added} generations\n')

    except Exception as e:
        sys.stderr.write(f'ERROR: {e}\n')
        return -1

    return 0


if __name__ == '__main__':
    sys.exit(main())

