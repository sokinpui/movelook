# move the elastic search related code to this file
from elasticsearch import Elasticsearch
import yaml

class Database:
    def __init__(self, database_config):
        # self.config = self.read_config(config_file)
        self.host_info = database_config['host']
        self.__get_host()

    def read_config(self, config_file):
        print(f"Reading config from {config_file}")
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)

    def __get_host(self):
        self.scheme = self.host_info['scheme']
        self.host = self.host_info['host']
        self.port = self.host_info['port']
        print(f"Elasticsearch Connecting to {self.scheme}://{self.host}:{self.port}")
        return [{"scheme": self.scheme, "host": self.host, "port": self.port}]

    def connect(self):
        host = self.__get_host()
        try:
            self.es = Elasticsearch(host)
            info = self.es.info()
            print("Elasticsearch is connected. Cluster info:", info)
        except Exception as e:
            print("Error connecting to Elasticsearch:", str(e))

    def insert(self, index, body):
        self.es.index(index=index, body=body)

    def insert_log_line(self, system, log, line, path, lineNumber, timestamp):
        doc = {
            'system': system,
            'log': log,
            'details': {
              'line': line,
              'path': path,
              'lineNumber': lineNumber,
              'timestamp': timestamp,
              'processed': False,
            }
        }
        self.insert(system, doc)

    # clear all the whole database
    def clear(self, index):
        self.es.indices.delete(index=index)
        print(f"Index {index} is deleted")

    def clear_database(self):
        self.es.indices.delete(index="_all")
        print("All indices are deleted")

    # mapping = {
    #         "properties": {
    #             "system": { "type": "keyword" },
    #             "log": { "type": "text" },
    #             "line": { "type": "text" },
    #             "path": { "type": "text" },
    #             "lineNumber": { "type": "integer" },
    #             "timestamp": { "type": "date" },
    #             "processed": { "type": "boolean" }
    #     }
    # }

