from abc import ABC, abstractmethod

class Database(ABC):
    @abstractmethod
    def insert(self, data : dict):
        pass

    @abstractmethod
    def search(self, query : dict):
        pass

    def update(self, query : dict, data : dict):
        pass

class ElasticsearchDatabase(Database):

    def __init__(self):
        self._connect()

    def _connect(self):
        print("Connecting to Elasticsearch")

    def insert(self, data : dict):
        print(f"Inserting data into Elasticsearch: {data}")

    def search(self, query : dict):
        print(f"Searching data in Elasticsearch: {query}")
