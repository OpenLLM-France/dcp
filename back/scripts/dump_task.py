#!/usr/bin/env python3

import sys
import os
import argparse
import json

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'app'))

from database import get_db
from service import DataCollectionPlatform


def main():
    parser = argparse.ArgumentParser(description='Dump task data to .json')
    parser.add_argument('-t', '--task-id', type=str, help='Task id')
    args = parser.parse_args()

    db = next(get_db())
    srv = DataCollectionPlatform()

    prompts = srv.get_prompts_for_task(db, args.task_id)
    out = {
        'prompts': {},
        'params': {},
        'bots': {}
    }

    known_users = {}

    for prompt in prompts:
        generations = srv.get_generations_for_prompt(db, prompt['id'])
        out['prompts'][prompt['id']] = {
            'prompt': prompt['text'],
            'generations': {},
            'task_instances': {}
        }
        for generation in generations:
            params_id = generation['params_id']
            if params_id not in out['params']:
                out['params'][params_id] = {}
            out['prompts'][prompt['id']]['generations'][generation['id']] = {
                'text': generation['text'],
                'params_id': generation['params_id']
            }

        task_instances = srv.get_task_instances_for_prompt(db, prompt['id'])
        for ti in task_instances:
            votes = srv.get_votes_for_task_instance(db, ti['id'])
            tags = srv.get_tags_for_task_instance(db, ti['id'])

            tags_by_genid = {
                ti['generation_a_id']: [],
                ti['generation_b_id']: []
            }
            for item in tags:
                tags_by_genid[item['generation_id']].append({
                    'action': '+' if item['action'] else '-',
                    'label': item['label'],
                    'timestamp': item['timestamp']
                })
                
            out['prompts'][prompt['id']]['task_instances'][ti['id']] = {
                'user_id': ti['user_id'],
                'generation_a_id': ti['generation_a_id'],
                'generation_b_id': ti['generation_b_id'],
                'timestamp': ti['timestamp'],
                'votes': votes,
                'tags': tags_by_genid
            }

            if ti['user_id'] not in known_users:
                known_users[ti['user_id']] = True
                bot_info = srv.get_bot_info(db, ti['user_id'])
                if bot_info is not None:
                    out['bots'][ti['user_id']] = bot_info
            
    print(json.dumps(out, ensure_ascii=False, sort_keys=True, indent=4))


if __name__ == '__main__':
    sys.exit(main())

