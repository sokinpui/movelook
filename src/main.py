import argparse
from collector import Collector
from analyzer import Analyzer
import es_engine
import time

# cli entry interface for the program

# default_config in the parent directory of this file

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
        self.__parsed_args = self.handle_args()

    def cmd_start(self):
        while True:
            if self.__parsed_args.no_collect == False:
                self.start_collector(self.__parsed_args.config)
            if self.__parsed_args.no_regex == False:
                self.start_analyzer(self.__parsed_args.config)
            if self.__parsed_args.no_loop == True:
                break
            time.sleep(120)

    def start_collector(self, config):
        collector = Collector(config)
        collector.start_collect()

    def start_analyzer(self, config):
        analyzer = Analyzer(config)
        analyzer.regex_batch_search()

    def handle_args(self):
        arg_parser = argparse.ArgumentParser(
                description=program_desc,
                # allow newines inserted in help text
                formatter_class=argparse.RawTextHelpFormatter
        )
        arg_parser.add_argument('action', help=action_help_msg, choices=actions)
        arg_parser.add_argument('-c', '--config', help='Path to config file', required=True)
        arg_parser.add_argument('-L', '--no-collect', help='ignore log collect', action='store_true', default=False, required=False)
        arg_parser.add_argument('-R', '--no-regex', help='ignore regex search', action='store_true', default=False, required=False)
        arg_parser.add_argument('-N', '--no-loop', help='run only once', action='store_true', default=False, required=False)
        parsed_args = arg_parser.parse_args()

        print(parsed_args)

        return parsed_args

def main():
    service = Service()
    service.cmd_start()
    pass

if __name__ == '__main__':
    main()
