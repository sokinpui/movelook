import datetime
from utils.timer import Timer
import yaml

def __handle_operation(search_query, op):
    # concatate the pattern with "and"
    return f' {op} '.join(p for p in search_query['patterns'])

def __parser_to_doc(queries):
    doc = {}
    for insight_group, search_query in queries.items():
        print(search_query)
        if 'operation' in search_query:
            if search_query['operation'] == 'and':
                # append to the doc with the key as the insight name
                doc[insight_group] = __handle_operation(search_query, "and")
            elif search_query['operation'] == 'or':
                # append to the doc with the key as the insight name
                doc[insight_group] = __handle_operation(search_query, "or")
        else:
            doc[insight_group] = __handle_operation(search_query, "or")
    return doc


# TODO: different pattern should store in different index, give good index name

class InsightEngine:
    def __init__(self):
        self.debug = False
        self.is_db_set = False

    def read_config(self, config_file):
        with open(config_file, 'r') as f:
            self.config = yaml.safe_load(f)
            self.queries = self.config['insightEngine'].pop('interval', None)
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

    def search_all_pattern(self):
        patterns = __parser_to_doc(self.queries)
        pass

    def search_pattern(self, target):
        pass

  # mark processed flag as true
    def mark_processed(self):
        pass

    def get_processed_flag(self):
        pass
