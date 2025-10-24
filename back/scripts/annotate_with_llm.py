#!/usr/bin/env python3

import sys
import os
import argparse
import json
import requests
import re

from openai_api_cache import OpenAICached


tmpl = '''
Agissez comme un juge expert chargé d'évaluer des paires de réponses générées par un modèle de langage. Votre tâche consiste à comparer deux complétions (complétion_1 et complétion_2) produites en réponse à un même texte déclencheur (prompt), puis à attribuer une note selon les critères suivants :

    Pertinence : À quel point la réponse correspond au contexte et à l'intention du prompt ?

    Cohérence : La réponse est-elle logique, bien structurée et exempte de contradictions ?

    Qualité linguistique : La réponse utilise-t-elle une grammaire, une syntaxe et un vocabulaire corrects ?

    Originalité : La réponse évite-t-elle les répétitions inutiles et apporte-t-elle une valeur ajoutée créative ?

    Utilité : La réponse est-elle informative, claire et adaptée à l'utilisateur cible ?

Après analyse, choisissez une seule des options suivantes :

    -3 : La première complétion est beaucoup meilleure que la seconde.

    -2 : La première complétion est meilleure que la seconde.

    -1 : La première complétion est légèrement meilleure que la seconde.

    0 : Les deux complétions sont équivalentes en qualité.

    1 : La deuxième complétion est légèrement meilleure que la première.

    2 : La deuxième complétion est meilleure que la première.

    3 : La deuxième complétion est beaucoup meilleure que la première.

    -100 : Les deux complétions sont également mauvaises (gravement défaillantes).

Consignes strictes :

    Ne justifiez pas votre choix.

    Répondez uniquement par le code numérique (exemple : 2, -3, 0, -100).

Prompt (texte déclencheur) :
%s

Complétion 1 :
%s

Complétion 2 :
%s

Annotation :
'''


acceptable_answers = [ -100, -3, -2, -1, 0, 1, 2, 3 ]


def create_bot_session_id(url, model_name, prompt_template, config):
    response = requests.post(f'{url}/create_bot_session', data = json.dumps({
        'model_name': model_name,
        'prompt_template': prompt_template,
        'config': json.dumps(config)
    }))

    if response.ok:
        try:
            session_id = response.json()['session_id']
            return session_id
        except Exception as e:
            sys.stderr.write(f'ERROR: {e}\n')
            sys.exit(-1)

    sys.stderr.write(f'ERROR: can\'t get session_id\n')
    sys.exit(-1)


def main():
    parser = argparse.ArgumentParser(description='Annotate task with LLM as a judge')
    parser.add_argument('-t', '--task-id', required=True, type=str, help='Task id')
    parser.add_argument('-u', '--url', required=True, type=str, help='Annotation API')
    parser.add_argument('-e', '--endpoint-url', required=True, type=str, help='LLM endpoint URL')
    parser.add_argument('-k', '--api-key', default='sk', type=str, help='Endpoint API key')
    parser.add_argument('-m', '--model', required=True, type=str, help='Model name')
    parser.add_argument('-r', '--temperature', default=0.0, type=float, help='Generation temperature')
    parser.add_argument('-c', '--cache-dir', default='./apicache/', type=str, help='API cache dir')
    args = parser.parse_args()

    api = OpenAICached(args.endpoint_url, args.api_key, args.model, f'./{args.cache_dir}/{args.model}.json')
    if args.model not in [ v.id for v in api.models() ]:
        print(api.models())
        sys.stderr.write(f'ERROR: no model \"{args.model}\" on the endpoint \"{args.endpoint_url}\"\n')
        return -1

    session_id = create_bot_session_id(args.url, args.model, tmpl, { 'temperature': args.temperature })

    url = f'{args.url}/task/{args.task_id}/next?session_id={session_id}'
    while True:
        response = requests.post(url, data = {}, cookies={'session_id': session_id})
        if response.ok:
            try:
                data = response.json()
                prompt = tmpl % (data['prompt'], data['generations'][0]['text'], data['generations'][1]['text'])
                ans = api.generate(prompt, args.temperature, 1)
                for item in ans:
                    item = item.strip()
                    tok = re.split(r'\s+', item)
                    try:
                        code = int(tok[0])
                    except Exception as e:
                        sys.stderr.write(f'ERROR: {e}\n')
                        break
                    if code in acceptable_answers:
                        dcp_url = f'{args.url}/task/vote'
                        dcp_data = {
                            'task_instance_id': data['task_instance_id'],
                            'generation_a_id': data['generations'][0]['id'],
                            'generation_b_id': data['generations'][1]['id'],
                            'value': code
                        }
                        headers = { 'Content-Type': 'application/json', 'User-Agent': 'annotate_with_llm.py' }
                        dcp_response = requests.post(dcp_url, data=json.dumps(dcp_data), headers=headers, cookies={'session_id': session_id})
                        if not dcp_response.ok:
                            sys.stderr.write(f'ERROR: request to \'{dcp_url}\' gave {dcp_response.code}\n')
                            return -1
                    else:
                        sys.stderr.write(f'Can\'t parse: {item}\n')
                        break
            except Exception as e:
                sys.stderr.write(f'ERROR: {e}\n')
                return -1
            api.save()
        else:
            sys.stderr.write(f'ERROR: {response}\n')
            return -1

    return 0


if __name__ == '__main__':
    sys.exit(main())

