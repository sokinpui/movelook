import argparse
import os
from collector import Collector
from analyzer import Analyzer
import es_engine
import time
from multiprocessing import Process

# default_config in the parent directory of this file
default_config = os.path.join(os.path.dirname(__file__), '..', 'config.yml')

# ================helper messages================
program_desc = "Log analysis tools"
action_help_msg = """
    start: start the service
    stop: stop the service
    status: check the status of the service
"""

actions = [
    'start',
    'stop',
    'status'
]

# ===============================================

class Service:
    def __init__(self):
        self.__running = False

    def start(self, config_path, skip_collector=True, skip_regex=True):
        self.__running = True
        while self.__running:
            # es_engine.start_container()
            print("start service ...")

            if not skip_collector:
                collector = Collector(config_path)
                collector.process()
            else:
                print('skip log collection...')
            if not skip_regex:
                analyzer = Analyzer(config_path)
                analyzer.regex_batch_search()
            else:
                print('skip regex search...')
            time.sleep(2)
        self.__running = False

    def stop(self):
        print('Stopping service...')
        self.__running = False

    def status(self):
        print('Service is running')
        if self.__running:
            print('Service is running')

def handle_args(args):
    arg_parser = argparse.ArgumentParser(
            description=program_desc,
            # allow newines inserted in help text
            formatter_class=argparse.RawTextHelpFormatter
            )
    arg_parser.add_argument('action', help=action_help_msg, choices=actions)
    arg_parser.add_argument('-c', '--config', help='Path to config file', default=default_config, required=False)
    arg_parser.add_argument('-L', '--no-collect', help='ignore log collect', action='store_true', default=False, required=False)
    arg_parser.add_argument('-R', '--no-regex', help='ignore regex search', action='store_true', default=False, required=False)
    args = arg_parser.parse_args()

    service = Service()

    # cannot stop
    if args.action == 'start':
        p = Process(target=service.start, args=(args.config, args.no_collect, args.no_regex))
        print(p)
        p.start()
        # save p obj into file
        with open('ml-pid.txt', 'w') as f:
            f.write(str(p.pid))
    elif args.action == 'stop':
        service.stop()
        # read p obj from file
        with open('ml-pid.txt', 'r') as f:
            pid = int(f.read())
        print('kill process with pid: {}'.format(pid))
        os.system('kill -9 {}'.format(pid))
    elif args.action == 'status':
        service.status()


