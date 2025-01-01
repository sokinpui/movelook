import datetime
from .timer import Timer
import yaml
from elasticsearch import Elasticsearch, helpers
from es_client import ESClient

valid_timestamp_range = 7

# TODO: different pattern should store in different index, give good index name

with open('config.yml', 'r') as f:
    config = yaml.safe_load(f)
    interval = config['extractor']['interval']
    action_msg_index = config['action_hanlder']['index']

class Extractor:
    def __init__(self, config):
        self.interval = interval
        self.timer = Timer(self.interval)
        self.es_client = ESClient.get_instance()
        self.read_config(config)

    def read_config(self, config_file):
        with open(config_file, 'r') as f:
            self.config = yaml.safe_load(f)

    def start(self):
      self.timer.start()

    def set_function(self, function, *args, **kwargs):
        self.timer.set_function(function, *args, **kwargs)

    def stop(self):
        if self.timer.function is not None:
            self.timer.stop()

    def regex_search(self):
        regex_patterns = self.config['patterns']['regex']

        regex_match_indices = []

        for pattern_group in regex_patterns:
            name = pattern_group['name']
            pattern = pattern_group['pattern']
            action = pattern_group['action']
            query ={
              "query": {
                "regexp": {
                  "line": pattern
                }
              }
            }
            # :TODO: make "logs_raw" a Global variable
            response = self.es_client.search(index="logs_raw", body=query)

            # convert all space to underscore and lowercase
            index = name.replace(" ", "_").lower()
            if not self.es_client.indices.exists(index=index):
                self.es_client.indices.create(index=index)

            # store matched logs
            actions = []
            for hit in response['hits']['hits']:
                action = {
                    "_index": index,
                    "_id": hit['_id'],  # Optional: preserve the original document ID
                    "_source": hit['_source']
                }
                actions.append(action)
            if actions:
                helpers.bulk(self.es_client, actions)
                print(f"Inserted {len(actions)} documents")
            else:
                print("No documents to insert")

            regex_match_indices.append(index)

            # put message if pattern is found
            if response['hits']['total']['value'] > 0:
                msg = {
                    "timestamp": datetime.datetime.now(),
                    "action": action,
                    "message": name
                }
                self.es_client.index(index=action_msg_index, body=msg)

        return regex_match_indices
