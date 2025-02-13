import datetime

from pydantic import Json, NonNegativeFloat
import yaml
import os
from elasticsearch import helpers
from es_engine import ESClient

valid_timestamp_range = 7

# from ollama import chat, ChatResponse

# llm chat helper function
# def _llm_chat(model, prompt):
#     response : ChatResponse = chat(model=model, messages=[{
#             'role': 'user',
#             'content': prompt
#         }
#     ])
#     return response


dir_path = os.path.dirname(os.path.realpath(__file__))
config_path = os.path.join(dir_path, 'devconfig.yml')
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)
action_queue_index = config['action_hanlder']['index']
search_index = config['collector']['index']

class Analyzer:
    def __init__(self, config):
        self.es = ESClient().get_instance()
        self.read_config(config)

    def read_config(self, config_file):
        with open(config_file, 'r') as f:
            self.config = yaml.safe_load(f)

    # search for patterns in the logs and then insert them into the index
    # insert the message into the action index if the pattern is found

    # regex_obj: dict that store the
    def regex_batch_search(self):
        regex_objs = self.config['patterns']['regex']
        for regex_obj in regex_objs:
            self.regex_search(regex_obj)

    def regex_search(self, regex_obj):
        print(regex_obj)

        regex_match_indices = []

        name = regex_obj['name']
        pattern = regex_obj['pattern']
        action = regex_obj['action']
        query ={
          "query": {
            "regexp": {
                "line": {
                    "value": pattern,
                    "flags": "ALL"
                }
            }
          }
        }
        print(f"Searching for {name} pattern")
        response = self.es.search(index=search_index, body=query)

        # convert all space to underscore and lowercase
        index = name.replace(" ", "_").lower()
        if not self.es.indices.exists(index=index):
            print(f"Creating index {index}")
            self.es.indices.create(index=index)

        # store matched logs
        actions = []
        for hit in response['hits']['hits']:
            action = {
                "_index": index,
                "_id": hit['_id'],  # Optional: preserve the original document ID
                "_source": hit['_source']
            }
            # print matched logs_raw
            actions.append(action)
        if actions:
            helpers.bulk(self.es, actions)
            print(f"Inserted {len(actions)} documents")
        else:
            print(f"No documents to insert for {name}")


        # put message if pattern is found
        if response['hits']['total']['value'] > 0:
            regex_match_indices.append(index)
            msg = {
                "timestamp": datetime.datetime.now(),
                "action": action,
                "message": name
            }
            self.es.index(index=action_queue_index, body=msg)

        return regex_match_indices

