import importlib
from datetime import datetime

from collector import Collector
from analyzer import Analyzer
from es_engine import ESClient
from es_engine import start_container, start_kibana_gui, remove_container

import os
import yaml
import sys

# can you write a simple shell for me?
# R to reload the test() function
# r to run the test() function

PRELOADED_MODULES = set()

def run_test():
    print("====================================")
    print(f'Running test() at {datetime.now()}')
    print()
    try:
        test()
    except Exception as e:
        print(f'An error occurred: {e}')
    print()
    print("====================================")
    print()

def reload_test():
    for module_name in list(sys.modules.keys()):
        # Skip built-in modules and the main module
        if not module_name.startswith('__') and not module_name.startswith('builtins'):
            module = sys.modules[module_name]
            # Reload the module
            importlib.reload(module)
    print("====================================")
    print('=========Reloaded mytest.py=========')
    print("====================================")
    print()

def reload_all_modules():
    from sys import modules
    import importlib

    for module in set(modules.values()) - PRELOADED_MODULES :
        try :
            importlib.reload(module)
        except :
            # there are some problems that are swept under the rug here
            pass

    print("====================================")
    print('=========Reloaded mytest.py=========')
    print("====================================")
    print()

def main():
    while True:
        cmd = input('Enter command: ')
        if cmd == 'R':
            reload_all_modules()
        elif cmd == 'r':
            run_test()
        elif cmd == "rr":
            reload_all_modules()
            run_test()
        elif cmd == 'q':
            print('Exiting...')
            break
        else:
            print('Invalid command!')



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
    test_extractor()

if __name__ == '__main__':
    main()

