import datetime
from .timer import Timer
import yaml
from elasticsearch import Elasticsearch, helpers
from es_client import ESClient

valid_timestamp_range = 7

# :NOTE: impelement after the basic regex search is done
# operator = { 'and': 'must', 'or': 'should' }
#
# def handle_operation(search_query, op):
#     # Extract patterns from the search query
#     patterns = search_query.get('patterns', [])
#
#     # Use a 'must' clause for 'and' operator (all patterns must match)
#     query = {
#         "bool": {
#             operator[op]: []
#         }
#     }
#     for pattern in patterns:
#         query["bool"]["must"].append({
#             "regex": {
#                 "field_name": pattern  # Replace 'field_name' with the actual field you want to search
#             }
#         })
#     return query
#
# def parser_to_doc(queries):
#     doc = {}
#     for insight_group, search_query in queries.items():
#         print(search_query)
#         if 'operator' in search_query:
#             if search_query['operator'] == 'and':
#                 # append to the doc with the key as the insight name
#                 doc[insight_group] = handle_operation(search_query, "and")
#             elif search_query['operator'] == 'or':
#                 # append to the doc with the key as the insight name
#                 doc[insight_group] = handle_operation(search_query, "or")
#         else:
#             doc[insight_group] = handle_operation(search_query, "or")
#     return doc



# TODO: different pattern should store in different index, give good index name

with open('config.yml', 'r') as f:
    config = yaml.safe_load(f)
    interval = config['extractor']['interval']
    f.close()

class Extractor:
    def __init__(self):
        self.interval = interval
        self.timer = Timer(self.interval)
        self.es_client = ESClient.get_instance()

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

        return regex_match_indices
