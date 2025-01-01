from .timer import Timer

from .log_collector import Collector
from .pattern_extractor import Extractor
from .action_handler import ActionHandler
from .data_cleaner import BufferManager
import os
import sys

import config_checker
import start_elasticsearch

config_checker.config_checker()
start_elasticsearch.start_elasticsearch()

# $HOME/.config/ml/config.yml
config = '$HOME/.config/ml/config.yml'

collector = Collector(config)
extractor = Extractor(config)
action_handler = ActionHandler(config)
move2buffer = BufferManager(config)
trash_cleaner = BufferManager(config)

# can be configured in the config file
collector_timer = Timer(5 * 60)  # 5 minutes
extractor_timer = Timer(5 * 60)  # 5 minutes
action_handler_timer = Timer(5 * 60)  # 5 minutes
move2buffer_timer = Timer(10 * 60 * 24)  # 10 retention_days
trash_cleaner_timer = Timer(30 * 60 * 24)  # 30 retention_days

collector_timer.set_function(collector.process)
extractor_timer.set_function(extractor.regex_search)
action_handler_timer.set_function(action_handler.check_messages)
move2buffer_timer.set_function(move2buffer.move_to_buffer)
trash_cleaner_timer.set_function(trash_cleaner.cleanup_buffer)

# add logic to terminate the program
