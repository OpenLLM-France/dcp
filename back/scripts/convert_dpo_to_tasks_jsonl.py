#!/usr/bin/env python3

import sys
import os
import lzma
import argparse
import json


def main():
    parser = argparse.ArgumentParser(description='Convert DPO pairs')
    parser.add_argument('-i', '--input', required=True, type=str, help='Input file (.jsonl or .jsonl.xz)')
    args = parser.parse_args()

    try:
        if args.input.endswith('.jsonl'):
            fh = open(args.input, 'rt')
        elif args.input.endswith('.jsonl.xz'):
            fh = lzma.open(args.input, 'rt')
        else:
            sys.stderr.write(f'ERROR: don\'t know how to open {args.input}\n')
            return -1
 
        for line in fh:
            d = json.loads(line)
            prompt = ''
            if d['system'] is not None:
                prompt = d['system'].strip() + '\n\n'
            prompt += d['question']
            print(json.dumps({
                'prompt': prompt,
                'generations': [
                    {
                        'text': d['chosen'],
                        'params': {
                            'status': 'chosen'
                        }
                    },
                    {
                        'text': d['rejected'],
                        'params': {
                            'status': 'rejected'
                        }
                    }
                ]
            }, ensure_ascii=False))

    except Exception as e:
        sys.stderr.write(f'ERROR: {e}\n')
        return -1

    return 0


if __name__ == '__main__':
    sys.exit(main())

