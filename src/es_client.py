from elasticsearch import Elasticsearch

# TODO: work with ES security and authentication, cert and key files


class ESClient:

    def __init__(self):
        # self.es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
        self.instance = None

    def get_instance(self):
        self.instance = Elasticsearch('http://localhost:9200')

        return self.instance
