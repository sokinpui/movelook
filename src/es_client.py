from elasticsearch import Elasticsearch

class ESClient:
    _instance = None

    @staticmethod
    def get_instance():
        if ESClient._instance is None:
            print("Creating ESClient instance")
            ESClient()
        return ESClient._instance

    def __init__(self):
        if ESClient._instance is not None:
            raise Exception("This class is a singleton!")
        else:
            ESClient._instance = Elasticsearch(['http://localhost:9200'])  # Update with your ES details

# Usage
# es_client = ESClient.get_instance()
