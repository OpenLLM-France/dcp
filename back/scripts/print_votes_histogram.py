#!/usr/bin/env python3

import sys
import argparse
import json
import lzma
import logging

from typing import Dict, Any


def load_json(path: str) -> Dict[str, Any]:
    try:
        if path.endswith('.json'):
            with open(path, 'rt') as f:
                return json.load(f)
        elif path.endswith('.json.xz'):
            with lzma.open(path, 'rt') as f:
                return json.load(f)
        else:
            logging.error(f"Don't know how to open {path}")
            sys.exit(1)
    except (FileNotFoundError, json.JSONDecodeError, lzma.LZMAError) as e:
        logging.error(f"Failed to load file {path}: {e}")
        sys.exit(1)


def print_histogram(users_data: Dict[int, Dict[str, Any]]):
    for user_id, info in users_data.items():
        display_name = info['display_name']
        deterministic = info['deterministic']
        votes = info['votes']

        print(f'{display_name} (deterministic={deterministic})')
        total = sum(votes.values())

        for i in range(-3, 4):
            cnt = votes.get(i, 0)
            f = float(cnt) * 100 / total
            print(f'{user_id} \t  {i:2} \t {cnt:7} \t {f:2.2f}%')

        cnt = votes.get(-100, 0)
        f = float(cnt) * 100 / total
        print(f'{user_id} \t-100 \t {cnt:7} \t {f:2.2f}%')
        print()


def count_votes(data: Dict[str, Any]) -> Dict[int, Dict[str, Any]]:
    users = {}
    answer_by_user = {}

    for prompt_id, prompt_data in data['prompts'].items():
        generations = prompt_data['generations']
        task_instances = prompt_data['task_instances']

        for tid, ti in task_instances.items():
            if not ti['votes']:
                continue

            user_id = int(ti['user_id'])
            answer_by_user.setdefault(user_id, {'raw': {}, 'cnt': {}})

            if user_id not in users:
                deterministic = False
                display_name = f'user_{user_id}'
                if str(user_id) in data['bots']:
                    bot_info = data['bots'][str(user_id)]
                    display_name += f' model_name={bot_info["model_name"]}'
                    if 'config' in bot_info and 'temperature' in bot_info['config'] \
                        and 0 == bot_info['config']['temperature']:
                        deterministic = True
                    
                users[user_id] = {
                    'display_name': display_name,
                    'deterministic': deterministic
                }

            pair_id = ' '.join([prompt_id, ti['generation_a_id'], ti['generation_b_id']])

            for vote in ti['votes']:
                if users[user_id]['deterministic'] and pair_id in answer_by_user[user_id]['raw']:
                    if vote['answer'] not in answer_by_user[user_id]['cnt']:
                        raise
                    if vote['answer'] != answer_by_user[user_id]['raw'][pair_id]:
                        sys.stderr.write(f"{answer_by_user[user_id]['cnt'][vote['answer']]}\n")
                        raise
                    continue

                answer_by_user[user_id]['raw'][pair_id] = vote['answer']
                if vote['answer'] not in answer_by_user[user_id]['cnt']:
                    answer_by_user[user_id]['cnt'][vote['answer']] = 1
                else:
                    answer_by_user[user_id]['cnt'][vote['answer']] += 1

    return {uid: {**user_info, 'votes': answer_by_user[uid]['cnt']} for uid, user_info in users.items()}


def main():
    parser = argparse.ArgumentParser(description='Prints votes histogram per user')
    parser.add_argument('-i', '--input', type=str, required=True, help='.json(.xz) dump for one task')
    args = parser.parse_args()

    data = load_json(args.input)
    users_data = count_votes(data)
    print_histogram(users_data)


if __name__ == '__main__':
    sys.exit(main())

