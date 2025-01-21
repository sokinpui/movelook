import datetime

from pydantic import Json, NonNegativeFloat
from .timer import Timer
import yaml
from elasticsearch import Elasticsearch, helpers
from es_client import ESClient

valid_timestamp_range = 7

from ollama import chat, ChatResponse

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


            # put message if pattern is found
            if response['hits']['total']['value'] > 0:
                regex_match_indices.append(index)
                msg = {
                    "timestamp": datetime.datetime.now(),
                    "action": action,
                    "message": name
                }
                self.es_client.index(index=action_msg_index, body=msg)

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
            files = None

            # or use another llm agent to decide should a alert msg to be inserted
            response : ChatResponse = chat(model="llama3.2:3b", messages=[
                {
                    'role': 'user',
                    'content': f'answer either "yes" or "no"\ncontext/files/text:{files} \nquestion: {content}\n'
                    }
                ])

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
                self.es_client.index(index=action_msg_index, body=msg)

        return positives


