#!/usr/bin/env python3

import sys
import time
import json
import random
from openai import OpenAI


class OpenAICached:
    def __init__(self, base_url, api_key, model, cache_fn):
        self.client = OpenAI(base_url=base_url, api_key=api_key)
        self.cache = {}
        self.cache_fn = cache_fn
        self.model = model

        if cache_fn is not None:
            try:
                with open(cache_fn, 'r') as f:
                    self.cache = json.load(f)
            except FileNotFoundError as e:
                sys.stderr.write(f'WARNING: File {cache_fn} doesn\'t exist.\n')
            except Exception as e:
                sys.stderr.write(str(type(e)) + '\n')
                sys.stderr.write(str(e) + '\n')


    def save(self):
        with open(self.cache_fn, 'w') as f:
            json.dump(self.cache, f, ensure_ascii=False, indent=4)


    def generate(self, text, temperature, num):
        k = self._create_key(text, temperature)
        self._populate_cache(k, text, temperature, num)
        return random.sample(self.cache[k], num)


    def models(self):
        return self.client.models.list()


    def _create_key(self, text, temperature):
        return json.dumps({ 'prompt': text, 'temperature': temperature }, ensure_ascii=False, sort_keys=True)


    def _populate_cache(self, k, text, temperature, num):
        if k not in self.cache:
            self.cache[k] = []

        while len(self.cache[k]) < num:
            try:
                completion = self.client.chat.completions.create(model=self.model, \
                                messages=[{ 'role': 'user', 'content': text }], \
                                temperature=temperature)
                self.cache[k].append(completion.choices[0].message.content)
            except Exception as e:
                sys.stderr.write(str(e) + '\n')
                time.sleep(20)


