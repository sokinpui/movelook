import yaml
import datetime
from utils.repeatTimer import Timer

# read every lines in a log then insert to a database, the whole log file will insert into single field
# set a marker to mark the last line that has been read
# read from last marker + 1
# reset marker if last marker is greater than max line


class Collector:
    def __init__(self, collector_config, db):
        """
        collector_config = config['collector']
        """
        self.systems = collector_config['systems']
        self.interval = collector_config['interval']
        self.marker = {}
        self.readtime = {}
        self.es = db
        # self.marker_db_index = 'marker'

    def start(self):
      self.timer = Timer(self.interval, self.process)
      self.timer.start()

    def stop(self):
      self.timer.stop()

# read a yml config file
    def read_config(self, config_file):
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)

# the yml specifies log from which system, then which log
    def process(self):
        for system_name in self.systems:
            for log in self.systems[system_name]:
                self.__process_log(system_name, log)
                print()

    def __process_log(self, system, log):
        print(f"Reading {log} from {system}")
        path = self.systems[system][log]['path']
        marker = self.__get_marker(system, log)
        #print the log name and the system come from

        with open(path, 'r') as f:
            # self.readtime[(system, log)] = datetime.datetime.now()
            print(f"Last read time is {self.readtime[(system, log)]}")

            lines = f.readlines()

            if marker == len(lines):
              print("No update")
              return

            # reset marker if last marker is greater than No. of lines
            if marker > len(lines):
                marker = self.__reset_marker(system, log)


            for i in range(marker, len(lines)):
                print(lines[i])
                # insert to database
                index = system
                doc = {
                    'system': system,
                    'log': log,
                    'details': {
                      'line': lines[i],
                      'path': path,
                      'lineNumber': i,
                      # 'timestamp': self.readtime[(system, log)],
                      'timestamp': datetime.datetime.now(),
                      'processed': False,
                      }
                    }
                self.es.insert(index, doc)
            # update marker to last line
            self.__set_marker(system, log, len(lines))

    def __get_marker(self, system, log):
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
        return self.marker.get((system, log), 0)

    def __set_marker(self, system, log, marker):
        self.marker[(system, log)] = marker
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

    def __reset_marker(self, system, log):
        self.marker[(system, log)] = 0
        print(f"Reset marker to 0")
        return self.marker[(system, log)]

# test config reading, pring the config
if __name__ == '__main__':
  pass
