from .timer import Timer

from .log_collector import Collector
from .pattern_extractor import Extractor
from .action_handler import ActionHandler
from .data_cleaner import BufferManager
import os
import sys

import config_checker
import start_elasticsearch
import ollama_llm

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(filename='ml.log', format='%(levelname)s: %(asctime) %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)

# TODO: doesn't put any config file yet for convenience
# config_checker.config_checker()
# start_elasticsearch.start_elasticsearch()
ollama_llm.start_ollama()

# $HOME/.config/ml/config.yml
config = '$HOME/.config/ml/config.yml'

collector = Collector(config)
extractor = Extractor(config)
action_handler = ActionHandler(config)
move2buffer = BufferManager(config)
trash_cleaner = BufferManager(config)

def main():
    try:
        while True:
            # logging with timestamp
            logger.info('Starting the main process...')
            logger.info('Collector process started...')
            collector.process()
            logger.info('Collector process completed...')
            logger.info('Extractor process started...')
            extractor.regex_search()
            logger.info('Extractor process completed...')
            logger.info('Action Handler process started...')
            action_handler.check_messages()

    except KeyboardInterrupt:
        print('Exiting...')
        logger.info('Exiting...')
        sys.exit(0)
    except Exception as e:
        print(f'An error occurred: {e}')
        logger.error(f'An error occurred: {e}')
        sys.exit(1)


if __name__ == '__main__':
    main()

# can be configured in the config file
# collector_timer = Timer(5 * 60)  # 5 minutes
# extractor_timer = Timer(5 * 60)  # 5 minutes
# action_handler_timer = Timer(5 * 60)  # 5 minutes
# move2buffer_timer = Timer(10 * 60 * 24)  # 10 retention_days
# trash_cleaner_timer = Timer(30 * 60 * 24)  # 30 retention_days
# collector_timer.set_function(collector.process)
# extractor_timer.set_function(extractor.regex_search)
# action_handler_timer.set_function(action_handler.check_messages)
# move2buffer_timer.set_function(move2buffer.move_to_buffer)
# trash_cleaner_timer.set_function(trash_cleaner.cleanup_buffer)
#
# # add logic to terminate the program
