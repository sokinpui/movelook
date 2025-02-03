import datetime

from pydantic import Json, NonNegativeFloat
from ptimer import Timer
import yaml
import os
from elasticsearch import helpers
from es_engine import ESClient

valid_timestamp_range = 7

from ollama import chat, ChatResponse

# llm chat helper function
def _llm_chat(model, prompt):
    response : ChatResponse = chat(model=model, messages=[{
            'role': 'user',
            'content': prompt
        }
    ])
    return response


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

    def llm_search(self):
        llm_searches = self.config['patterns']['llm']
        # positive means llm agent answer yes to the question
        positives = []

        for prompt_obj in llm_searches:
            name = prompt_obj['name']
            content = prompt_obj['prompt']
            action = prompt_obj['action']

            # concatenate all the file into one string within 128k characters
            # files = concatenate_files_in_es()
            related_text = None

            # or use another llm agent to decide should a alert msg to be inserted
            prompt = f'answer either "yes" or "no"\ncontext/files/text:{related_text} \nquestion: {content}\n'
            response = _llm_chat("llama3.2:3b", prompt)

            answer = response['message']['content']

            if 'yes' in answer or "Yes" in answer:
                # mark the name since it is positives
                # consist the name to lower case to es regex search implementation
                # TODO: insert the prompt to elasticsearch?
                positives.append(name.lower())
                # store the message
                msg = {
                    "timestamp": datetime.datetime.now(),
                    "action": action,
                    "message": name
                }
                self.es.index(index=action_queue_index, body=msg)

        return positives


    # TODO: how to feed text longer than context length

    def __filter_related(self, question):
        related_files = []

        # fetch all file nmaes from es
        query = {
                "aggs": {
                    "unique_files": {
                        "terms": {
                            "field": "path"
                        }
                    }
                }
            }
        response = self.es.search(index="logs_raw", body=query)
        files = []
        for file in response['aggregations']['unique_files']['buckets']:
            files.append(file['key'])

        prompt = f'return a python list to me\nQuestion: {question}\nFiles: {related_files}'
        related_files = _llm_chat("llama3.2:3b", prompt)

        return related_files

