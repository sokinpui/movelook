from collector import Collector
from analyzer import Analyzer
from es_engine import ESClient
from es_engine import start_container, start_kibana_gui, remove_container
from ollama_llm import main

import docker
import os
import subprocess
import yaml
import time
import requests


home_dir = os.getenv('HOME')
config = f'{home_dir}/work/ml/config.yml'

with open("devconfig.yml", 'r') as f:
    devconfig = yaml.safe_load(f)

def test_collector():
    collector = Collector(config)
    collector.process()

def test_extractor():
    extractor = Analyzer(config)
    extractor.regex_batch_search()

def test_es_engine():
    es = start_container()

def rm_containers():
    names = []
    names.append(devconfig['docker']['es']['name'])
    names.append(devconfig['docker']['kibana']['name'])
    for name in names:
        print(f'Removing container {name}')
        remove_container(name)

# wait logic

def test():
    # test_es_engine()
    # start_kibana_gui()
    # test_collector()

    # regex pattern return by llm
    # string = main()
    # regex_obj = {
    #     "name": "test",
    #     "pattern": string,
    #     "action": "test"
    # }

    # extractor = Analyzer(config)
    # extractor.regex_search(regex_obj)
    test_extractor()

test()

# while True:
#     try:
#         res = requests.get('http://localhost:9200')
#         print('ES is up!')
#         break
#     except requests.exceptions.ConnectionError:
#         print('Waiting for ES to start...')
#         time.sleep(1)
#     except Exception as e:
#         print(f'An error occurred: {e}')
#         break

# test_docker()
