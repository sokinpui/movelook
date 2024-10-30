import datetime
from utils.timer import Timer
import yaml

def __and_operation(patterns):
    patterns = patterns[1:]
    # concatate the pattern with "and"
    return ' and '.join(p for p in patterns if p != 'operation')

def __parser(query):
    p = query['pattern']
    # if p[0] is a dict and their is a key "operation" in it:
    if isinstance(p[0], dict) and 'operation' in p[0]:
        # if operation is "and"
        if p[0]['operation'] == 'and':
            return __and_operation(p)
    return ' or '.join(p for p in query['pattern'])

# TODO: different pattern should store in different index, give good index name

class InsightEngine:
    def __init__(self):
        self.debug = False
        self.is_db_set = False

    def read_config(self, config_file):
        with open(config_file, 'r') as f:
            self.config = yaml.safe_load(f)
            self.queries = self.config['insightEngine']
            self.interval = self.config['insightEngine']['interval']
            self.index = self.config['insightEngine']['index']
            self.timer = Timer(self.interval)

    def set_db(self, db):
        if self.is_db_set:
            raise Exception("Database already set")
        self.es = db
        self.is_db_set = True

    def start(self):
      self.timer.start()

    def set_function(self, function, *args, **kwargs):
        self.timer.set_function(function, *args, **kwargs)

    def stop(self):
        if self.timer.function is not None:
            self.timer.stop()

    def search(self):
        pass

    def pattern_search(self, target):
        pass

  # mark processed flag as true
    def mark_processed(self):
        pass

    def get_processed_flag(self):
        pass
