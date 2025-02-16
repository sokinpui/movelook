import yaml
import datetime
import os
from es_engine import ESClient

# read every lines in a log then insert to a database, the whole log file will insert into single field
# set a marker to mark the last line that has been read
# read from last marker + 1
# reset marker if last marker is greater than max line

# try:
#     with open('config.yml', 'r') as f:
#         config = yaml.safe_load(f)
# except FileNotFoundError:
#     print("Error: config.yml file not found.")
# except KeyError as e:
#     print(f"Error: Missing key in config.yml: {e}")
# except yaml.YAMLError as exc:
#     print(f"Error parsing YAML: {exc}")

import json
from pprint import pprint
import os
import time

# from dotenv import load_dotenv
from elasticsearch import Elasticsearch

# load_dotenv()

dir_path = os.path.dirname(os.path.realpath(__file__))
dev_config_path = os.path.join(dir_path, 'devconfig.yml')
with open(dev_config_path, 'r') as f:
    devconfig = yaml.safe_load(f)

class Collector:
    def __init__(self, config):
        self.marker = {}
        self.readtime = {}
        # self.timer.set_function(self.process)
        # self.marker_db_index = 'marker'
        self.es = ESClient().get_instance()
        # client_info = self.es.info()
        # print('Connected to Elasticsearch!')
        # pprint(client_info)
        self.read_config(config)


# read a yml config file
    def read_config(self, config_file):
        with open(config_file, 'r') as f:
            self.config = yaml.safe_load(f)
            self.directory = self.config['collector']['directory']

# read all the log file in self.directory recursively
# the log files may appear in different subdirectories
# get their path recursively
    def start_collect(self):
        print(f"Processing logs in {self.directory}")
        for root, dirs, files in os.walk(self.directory):
            for log in files:
                log_path = os.path.join(root, log)

                # self.process_log(log_path)
                marker = self.__get_marker(log_path)
                #print the log name and the system come from

                with open(log_path, 'r') as f:
                    # self.readtime[(system, log)] = datetime.datetime.now()

                    lines = f.readlines()

                    if marker == len(lines):
                      print(f"file {log_path} has not been updated")
                      return

                    # reset marker if last marker is greater than No. of lines
                    if marker > len(lines):
                        marker = self.__reset_marker(log_path)

                    for i in range(marker, len(lines)):
                        # insert to database
                        doc = {
                              'line': lines[i],
                              'line_length': len(lines[i]),
                              # store absolute path
                              'path': log_path,
                              'lineNumber': i,
                              'timestamp': datetime.datetime.now(),
                            }
                        self.es.index(index=devconfig['collector']['index'], body=doc)
                    print(f"Inserted {len(lines) - marker} lines of {log_path}")

                    # update marker to last line
                    self.__set_marker(log_path, len(lines))

    def __get_marker(self, log_path):
        return self.marker.get(log_path, 0)

    def __set_marker(self, log_path, marker):
        self.marker[log_path] = marker

    def __reset_marker(self, log_path):
        self.marker[log_path] = 0
        return self.marker[log_path]

def main():
    config_path = '../config.yml'
    collector = Collector(config_path)
    collector.start_collect()

# test config reading, pring the config
if __name__ == '__main__':
    main()

