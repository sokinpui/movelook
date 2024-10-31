import datetime
from utils.timer import Timer
import yaml
from config import *

operator = { 'and': 'must', 'or': 'should' }

def handle_operation(search_query, op):
    # Extract patterns from the search query
    patterns = search_query.get('patterns', [])

    # Use a 'must' clause for 'and' operator (all patterns must match)
    query = {
        "bool": {
            operator[op]: []
        }
    }
    for pattern in patterns:
        query["bool"]["must"].append({
            "regex": {
                "field_name": pattern  # Replace 'field_name' with the actual field you want to search
            }
        })
    return query

def parser_to_doc(queries):
    doc = {}
    for insight_group, search_query in queries.items():
        print(search_query)
        if 'operator' in search_query:
            if search_query['operator'] == 'and':
                # append to the doc with the key as the insight name
                doc[insight_group] = handle_operation(search_query, "and")
            elif search_query['operator'] == 'or':
                # append to the doc with the key as the insight name
                doc[insight_group] = handle_operation(search_query, "or")
        else:
            doc[insight_group] = handle_operation(search_query, "or")
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
        es_search_queries = parser_to_doc(self.queries)
        for insight_group, query in es_search_queries.items():
            query = {
                "query": query
            }
            res = self.es.search(index="raw_log", body=query)
            print(res)
        pass

    def search_pattern(self, target):
        pass

  # mark processed flag as true
    def mark_processed(self):
        pass

    def get_processed_flag(self):
        pass
