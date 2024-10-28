import yaml
import datetime
import os
from utils.timer import Timer

# read every lines in a log then insert to a database, the whole log file will insert into single field
# set a marker to mark the last line that has been read
# read from last marker + 1
# reset marker if last marker is greater than max line


class Collector:
    def __init__(self):
        self.marker = {}
        self.readtime = {}
        # self.timer.set_function(self.process)
        self.debug = False
        # self.marker_db_index = 'marker'

    def set_db(self, db):
        self.es = db

    def set_function(self, function):
        self.timer.set_function(function)

    def start(self):
      self.timer.start()

    def stop(self):
      self.timer.stop()

# read a yml config file
    def read_config(self, config_file):
        with open(config_file, 'r') as f:
            self.config = yaml.safe_load(f)
            self.directory = self.config['collector']['directory']
            self.interval = self.config['collector']['interval']
            self.timer = Timer(self.interval)

# read all the log file in self.directory recursively
# the log files may appear in different subdirectories
# get their path recursively
    def process(self):
        for root, dirs, files in os.walk(self.directory):
            for log in files:
                log_path = os.path.join(root, log)
                self.__process_log(log_path)

    def __process_log(self, log_path):
        marker = self.__get_marker(log_path)
        #print the log name and the system come from

        with open(log_path, 'r') as f:
            # self.readtime[(system, log)] = datetime.datetime.now()

            lines = f.readlines()

            if marker == len(lines):
              print("No update")
              return

            # reset marker if last marker is greater than No. of lines
            if marker > len(lines):
                marker = self.__reset_marker(log_path)


            for i in range(marker, len(lines)):
                # insert to database
                index = "logs_raw"
                doc = {
                      'line': lines[i],
                      'path': log_path,
                      'lineNumber': i,
                      # 'timestamp': self.readtime[(system, log)],
                      'timestamp': datetime.datetime.now(),
                      'processed': False,
                    }
                if (self.debug):
                    # print  log_path and lines[i] are the same
                    print(f"Reading log file: {log_path}")
                    # print marker
                    print(f"Marker: {marker}")
                else:
                    self.es.insert(index, doc)
            # update marker to last line
            self.__set_marker(log_path, len(lines))

    def __get_marker(self, log_path):
        # search the variable first, if not exist then search from database, if not exist, then create one
        # marker = self.marker.get((system, log), -1)
        # if marker == -1:
        #     # search from database
        #     # get the last line number
        #     query = {
        #   "query": {
        #     "bool": {
        #       "must": [
        #         {"match": {"system": system}},
        #         {"match": {"log": log}}
        #         ]
        #       }
        #     }
        #   }
        #     res = self.es.es.search(index=self.marker_db_index, body=query)
        #     if res['hits']['total']['value'] > 0:
        #         marker = res['hits']['hits'][0]['_source']['details']['line']
        #         self.marker[(system, log)] = marker
        #         print(f"Get marker from database: {marker}")
        #     else:
        #         self.marker[(system, log)] = 0
        #         print(f"Create new marker: 0")
        return self.marker.get(log_path, 0)

    def __set_marker(self, log_path, marker):
        self.marker[log_path] = marker
        print(f"Set marker to {marker}")
        # # set markder in new index
        # doc = {
        #     'system': system,
        #     'log': log,
        #     'details': {
        #       'line': marker,
        #       'timestamp': datetime.datetime.now(),
        #       }
        #     }
        # self.es.insert(self.marker_db_index, doc)

    def __reset_marker(self, log_path):
        self.marker[log_path] = 0
        print(f"Reset marker to 0")
        return self.marker[log_path]

# test config reading, pring the config
if __name__ == '__main__':
  pass
