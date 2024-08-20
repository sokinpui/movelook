import os
import yaml
import datetime
from utils.database import Database

# read every lines in a log then insert to a database, the whole log file will insert into single field
# set a marker to mark the last line that has been read
# read from last marker + 1
# reset marker if last marker is greater than max line


class Processor:
    def __init__(self, config):
        # self.config = self.read_config(config_file)
        self.config = config
        self.marker = {}
        self.readtime = {}
        self.es = Database(config)
        self.es.printa()

# read a yml config file
    def read_config(self, config_file):
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)

# the yml specifies log from which system, then which log
    def process(self):
        systems = self.config['systems']

        for system in systems:
            for log in systems[system]:
                self.process_log(system, log)
                print()

    def process_log(self, system, log):
        print(f"Reading {log} from {system}")
        path = self.config['systems'][system][log]['path']
        marker = self.get_marker(system, log)
        #print the log name and the system come from

        with open(path, 'r') as f:
            # format the last read time
            m_time = os.path.getmtime(path)
            dt_m = datetime.datetime.fromtimestamp(m_time)
            self.readtime[(system, log)] = dt_m
            print(f"Last read time is {self.readtime[(system, log)]}")

            lines = f.readlines()

            if marker == len(lines):
              print("No update")
              return

            # reset marker if last marker is greater than No. of lines
            if marker > len(lines):
                marker = self.reset_marker(system, log)


            for i in range(marker, len(lines)):
                print(lines[i])
                # insert to database
                index = system
                self.es.insert_log_line(index, log, lines[i], path, i, self.readtime[(system, log)])
            # update marker to last line
            self.set_marker(system, log, len(lines))

    def get_marker(self, system, log):
        # if it is new file, set marker to -1
        return self.marker.get((system, log), 0)

    def set_marker(self, system, log, marker):
        self.marker[(system, log)] = marker
        print(f"Set marker to {marker}")

    def reset_marker(self, system, log):
        self.marker[(system, log)] = 0
        print(f"Reset marker to 0")
        return self.marker[(system, log)]

    def print_marker(self):
        print(f"Marker: {self.marker}")

# test config reading, pring the config
if __name__ == '__main__':
    processor = Processor('config.yml')
    print(processor.config)
    # processor.process()
