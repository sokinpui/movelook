from collector import Collector
from analyzer import Analyzer
from es_engine import ESClient
from es_engine import start_container, start_kibana_gui

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
    extractor = Analyzer(config)
    extractor.regex_search()

def test_es_engine():
    es = start_container()

def test_regex_search():
    es = ESClient().get_instance()
    pattern = r"\b Dec \d{1,2}:\d{2}:\d{2} \S+ sshd\[([0-9]+)\]: (reverse|input_userauth_request|pam_unix\(sshd:auth\)) \(.*?\) failed - POSSIBLE BREAK-IN ATTEMPT!"
    query ={
      "query": {
        "regexp": {
          "line": f"{pattern}"
        }
      }
    }
    res = es.search(index='test-index', body=query)
    print(res)


# wait logic
test_es_engine()
# start_kibana_gui()
# test_collector()
# test_extractor()

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
