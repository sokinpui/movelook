from abc import ABC, abstractmethod

from logger import Logger

import requests
from elasticsearch import Elasticsearch
import config as cfg

from langchain_elasticsearch import ElasticsearchStore

class Database(ABC):

    @abstractmethod
    def insert(self, data: dict, identifier: str = None):
        """Insert data into the database. Identifier may specify a collection or index."""
        pass

    @abstractmethod
    def single_search(self, query: dict, identifier: str = None):
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

    @abstractmethod
    def set_vector_store(self, embeddings, index):
        """Set the vector store for the database."""
        pass

class ElasticsearchDatabase(Database):
    """
    provide some simple interface for common operations,
    but user can still access elasticsearch api via self.instance directly
    """

    def __init__(self):
        self._logger = Logger()
        self.instance = self._connect()
        self.vector_store = None

    def insert(self, data : dict, index : str):
        if self.instance is None:
            self._logger.error("Elasticsearch instance not initialized, please check if container is running")
            print("please check if Container is running")

        self.instance.index(index=index, body=data)

    def single_search(self, query : dict, index : str):
        """
        return single search result
        """
        query["size"] = 1
        if self.instance is None:
            self._logger.error("Elasticsearch instance not initialized")
            print("please check if Container is running")
            exit(1)

        result = self.instance.search(index=index, body=query)
        return result['hits']['hits']

    def scroll_search(self, query: dict, index: str):
        """
        Return all search results using the Scroll API.

        Args:
            query (dict): The Elasticsearch query body.
            index (str): The index to search in.

        Returns:
            list: A list of all matching documents (hits).
        """
        if self.instance is None:
            self._logger.error("Elasticsearch instance not initialized")
            print("please check if Container is running")
            exit(1)

        # Initial search with scroll
        scroll_size = 10000  # Number of documents per batch
        query_with_size = query.copy()  # Avoid modifying the original query
        if "size" not in query_with_size:
            query_with_size["size"] = scroll_size  # Set batch size

        all_hits = []
        response = self.instance.search(
            index=index,
            body=query_with_size,
            scroll="2m"  # Keep scroll context alive for 2 minutes
        )

        # Extract initial hits and scroll ID
        scroll_id = response["_scroll_id"]
        hits = response["hits"]["hits"]
        all_hits.extend(hits)

        # Continue scrolling until no more results
        while len(hits) > 0:
            response = self.instance.scroll(
                scroll_id=scroll_id,
                scroll="2m"  # Renew scroll context
            )
            scroll_id = response["_scroll_id"]
            hits = response["hits"]["hits"]
            all_hits.extend(hits)

        # Clean up scroll context (optional but good practice)
        self.instance.clear_scroll(scroll_id=scroll_id)

        return all_hits


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
        es_url = cfg.ELASTIC_SEARCH_URL
        try:
            requests.get(es_url)
            instance = Elasticsearch([es_url])
            self._logger.info("Connected to Elasticsearch")
            return instance
        except requests.exceptions.ConnectionError as e:
            self._logger.error(f"Error connecting to Elasticsearch: {e}")
            print("please check if Container is running")
            return None

    def set_vector_store(self, embeddings, index) -> ElasticsearchStore:
        try:
            vector_store = ElasticsearchStore(
                es_url=cfg.ELASTIC_SEARCH_URL,
                index_name=index,
                embedding=embeddings,
            )
            return vector_store
        except Exception as e:
            self._logger.error(f"Error setting vector store: {e}")
            exit(1)

    def random_sample(self, index : str, size : int):
        """
        return random sample of size from index
        """
        query = {
            "size": size,
            "query": {
                "function_score": {
                    "query": {"match_all": {}},
                    "random_score": {}
                }
            }
        }
        try:
            return self.instance.search(index=index, body=query)['hits']['hits']
        except Exception as e:
            self._logger.error(f"Error fetching random sample from index {index}: {e}")
            exit(1)

    def add_alias(self, index : str, alias : str, filter : dict = None):
        """
        add alias to index
        """
        query = {
            "actions": [
                {
                    "add": {
                        "index": index,
                        "alias": alias,
                        "filter": filter
                    }
                }
            ]
        }
        try:
            res = self.instance.indices.update_aliases(body=query)
            return res
        except Exception as e:
            self._logger.error(f"Error adding alias {alias} to index {index}: {e}")
            exit(1)


def main():
    es = ElasticsearchDatabase()

    res = es.random_sample("log_ssh", 100)

    for r in res:
        print(r["_source"]["content"])



if __name__ == "__main__":
    main()

