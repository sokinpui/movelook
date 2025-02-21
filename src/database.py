from abc import ABC, abstractmethod

from logger import Logger

import requests
from elasticsearch import Elasticsearch


class Database(ABC):

    @abstractmethod
    def insert(self, data: dict, identifier: str = None):
        """Insert data into the database. Identifier may specify a collection or index."""
        pass

    @abstractmethod
    def search(self, query: dict, identifier: str = None):
        """Search for data in the database. Identifier may specify a collection or index."""
        pass

    @abstractmethod
    def update(self, id, data: dict, identifier: str = None):
        """Update existing data in the database."""
        pass

    @abstractmethod
    def delete(self, id: id, identifier: str = None):
        """Delete data from the database."""
        pass

class ElasticsearchDatabase(Database):
    """
    provide some simple interface for common operations,
    but user can still access elasticsearch api via self.instance directly
    """

    def __init__(self):
        self._logger = Logger()
        self.instance = self._connect()

    def insert(self, data : dict, index : str):
        if self.instance is None:
            self._logger.error("Elasticsearch instance not initialized, please check if container is running")
            print("please check if Container is running")

        self.instance.index(index=index, body=data)

    def search(self, query : dict, index : str):
        if self.instance is None:
            self._logger.error("Elasticsearch instance not initialized")
            print("please check if Container is running")
            exit(1)

        result = self.instance.search(index=index, body=query)
        return result['hits']['hits']


    def update(self, id : str, data : dict, index : str,):
        if self.instance is None:
            self._logger.error("Elasticsearch instance not initialized")
            print("please check if Container is running")
            exit(1)

        self.instance.update(index=index, body=data, id=id)

    def delete(self, id : str, index : str):
        if self.instance is None:
            self._logger.error("Elasticsearch instance not initialized")
            print("please check if Container is running")
            exit(1)

        self.instance.delete(index=index, id=id)

    def _connect(self) -> Elasticsearch | None:
        try:
            requests.get('http://localhost:9200')
            instance = Elasticsearch([ 'http://localhost:9200' ])
            self._logger.info("Connected to Elasticsearch")
            return instance
        except requests.exceptions.ConnectionError as e:
            self._logger.error(f"Error connecting to Elasticsearch: {e}")
            print("please check if Container is running")
            return None

