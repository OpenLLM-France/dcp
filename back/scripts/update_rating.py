#!/usr/bin/env python3

import sys
import os
import argparse
import json
import time

from copy import deepcopy

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'app'))

from database import get_db
from service import DataCollectionPlatform


def normalize_task_instance(ti):
    if ti['generation_a_id'] < ti['generation_b_id']:
        return ti, False

    new_ti = deepcopy(ti)
    if new_ti['answer'] >= -3 and new_ti['answer'] <= 3:
        new_ti['answer'] *= -1
    new_ti['generation_a_id'] = ti['generation_b_id']
    new_ti['generation_b_id'] = ti['generation_a_id']

    return new_ti, True


def group_by_pairs(votes):
    pairs = {}
    for item in votes:
        if item['answer'] in [ -200 ]:
            continue

        ti, order_changed = normalize_task_instance(item)

        user_id = int(ti['user_id'])
        pair_id = ' '.join([ti['generation_a_id'], ti['generation_b_id']])

        if pair_id not in pairs:
            pairs[pair_id] = {}

        if user_id not in pairs[pair_id] or ti['timestamp'] > pairs[pair_id][user_id]['timestamp']:
            pairs[pair_id][user_id] = {
                'answer': ti['answer'],
                'timestamp': ti['timestamp']
            }

    return pairs


def aggregate_scores_majority_voting(stat):
    max_votes_freq = 0
    max_votes_values = []

    for val, freq in stat['freq'].items():
        if freq == max_votes_freq:
            max_votes_values.append(val)
        elif freq > max_votes_freq:
            max_votes_values = [ val ]
            max_votes_freq = freq

    return max_votes_values


def aggregate_scores(stat):
    return aggregate_scores_majority_voting(stat)


def collect_stat(pairs):
    stat = {}
    min_answers, max_answers = 100500, -100500
    for pair_id in pairs:
        min_answers = min(min_answers, len(pairs[pair_id]))
        max_answers = max(max_answers, len(pairs[pair_id]))
        dct = {}
        for user_id in pairs[pair_id]:
            val = pairs[pair_id][user_id]['answer']
            if val not in dct:
                dct[val] = 0
            dct[val] += 1
        stat[pair_id] = {
            'freq': dct,
        }
        stat[pair_id]['agg'] = aggregate_scores(stat[pair_id])

    return min_answers, max_answers, stat



def score_dist_abs(a: int, b: int):
    return abs(a - b) / 6


def score_dist_sign(a: int, b: int):
    assert(-3 <= a or a <= 3 or -100 == a)
    assert(-3 <= b or b <= 3 or -100 == b)
    aucune = [ 0, 0, 0, 0.5, 1, 1, 1 ]
    if a == b:
        return 0
    if -100 == a:
        return aucune[b + 3]
    if -100 == b:
        return aucune[a + 3]
    if 0 < a * b: #(a < 0 and b < 0) or (a > 0 and b > 0):
        return abs(a - b) / 10
    if 0 == a * b:
        return abs(a - b) / 5
    return 1


def score(a: int, b: int):
    #return score_dist_abs(a, b)
    return float(score_dist_sign(a, b))


def aggregate_scores_majority_voting(stat):
    max_votes_freq = 0
    max_votes_values = []

    for val, freq in stat['freq'].items():
        if freq == max_votes_freq:
            max_votes_values.append(val)
        elif freq > max_votes_freq:
            max_votes_values = [ val ]
            max_votes_freq = freq

    return max_votes_values


def aggregate_scores(stat):
    return aggregate_scores_majority_voting(stat)


def calculate_score(user_id, stat, pairs):
    diffs = []
    cnt = 0
    for pair_id in stat:
        p = pairs[pair_id]
        if user_id not in p or len(p) < 2:
            continue
        this_vote = p[user_id]['answer']
        temp_stat = deepcopy(stat[pair_id])
        temp_stat['freq'][this_vote] -= 1
        if 0 == temp_stat['freq'][this_vote]:
            del temp_stat['freq'][this_vote]
        d = min([ score(x, this_vote) for x in aggregate_scores(temp_stat) ])
        diffs.append(d)
        cnt += 1

    if cnt < 10:
        return None

    result = None
    if len(diffs) > 0:
        result = sum(diffs) / len(diffs)

    return result


def main():
    parser = argparse.ArgumentParser(description='Calculate user scores')
    parser.add_argument('-d', '--dry-run', type=str, help='Print scores but don\'t update the DB')
    args = parser.parse_args()

    db = next(get_db())
    srv = DataCollectionPlatform()
    votes = srv.get_all_votes(db)
    pairs = group_by_pairs(votes)
    min_answers, max_answers, stat = collect_stat(pairs)
    sys.stderr.write(f'min_answers={min_answers} max_answers={max_answers}\n')
    users = srv.get_user_bot(db)

    data = []
    for user in users:
        score = calculate_score(user['user_id'], stat, pairs)
        if score is not None:
            data.append({
                'user_id': user['user_id'],
                'score': score
            })

            count = srv.count_prompts_done_for_user(db, user['user_id'])
            print(f'{user["user_id"]} \t {score:.2f} \t {count} \t {user["model_name"]}')

    if not args.dry_run:
        try:
            before = time.time()
            srv.update_ratings(db, data)
            elapsed = time.time() - before
            sys.stderr.write(f'Update took {elapsed:.2f} seconds\n')
        except Exception as e:
            sys.stderr.write(f'ERROR while trying to bluk insert into Ratings:\n{e}\n')


if __name__ == '__main__':
    sys.exit(main())
