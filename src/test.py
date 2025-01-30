from log_collector import Collector
from pattern_extractor import Extractor
from es_engine import ESEngine
from es_engine import ESClient

import docker
import os
import subprocess
import yaml
import time
import requests


home_dir = os.getenv('HOME')
config = f'{home_dir}/work/ml/config.yml'


def test_collector():
    collector = Collector(config)
    collector.process()

def test_extractor():
    extractor = Extractor(config)
    extractor.regex_search()

def test_es_engine():
    es = ESEngine()

# wait logic
test_es_engine()

# NOTE: wait logic use in main.py
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
