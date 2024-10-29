#the data in ElasticSearch structure as following
        # doc = {
        #     'system': system,
        #     'log': log,
        #     'details': {
        #       'line': line,
        #       'path': path,
        #       'lineNumber': lineNumber,
        #       'timestamp': timestamp,
        #       'processed': False,
        #     }
        # }
import datetime
from utils.timer import Timer
import yaml

# TODO: different pattern should store in different index, give good index name

class Scanner:
    def __init__(self):
        """
        scanner_config = config['scanner']
        """
        pass

    def read_config(self, config_file):
        with open(config_file, 'r') as f:
            self.config = yaml.safe_load(f)
            self.pattern = self.config['scanner']['pattern']
            self.interval = self.config['scanner']['interval']
            self.index = self.config['scanner']['index']
            self.timer = Timer(self.interval)

    def set_db(self, db):
        if self.set_db:
            raise Exception("Database already set")
        self.es = db
        self.is_db_set = True

    def start(self):
      self.timer.start()

    def set_function(self, function, *args, **kwargs):
        self.timer.set_function(function, *args, **kwargs)

    def stop(self):
        if self.timer.function is not None:
            self.timer.stop()

    # TODO: the code below need modification
    def batch_search(self ):
        for system_name in self.systems:
            for log in self.systems[system_name]:
                for string in self.systems[system_name][log]:
                    if self.get_processed_flag(self.db,system_name, system_name, log):
                        continue
                    hits = self.regex_search(string, system_name, log)
                    self.mark_processed(self.db, system_name, system_name, log)
                    self.output_to_destination(hits, self.db, self.index)
                    print(f"Search {system_name} {log} with {string} done")
                    # print result
                    print(f"Found {hits['total']} hits")

    def simple_search(self, db, index, pattern, system_name="", log_name=""):
        hits = self.regex_search(pattern, system_name, log_name)
        self.mark_processed(db, index, system_name, log_name)
        self.output_to_destination(hits, db, index)

    def regex_search(self, search_string, system_name="", log_name=""):
        query = {
            "query": {
              "bool": {
                "must": [
                  {"regexp": {"details.line": search_string}}
                  ],
                "must": []
                }
              }
            }
# match system_name only if log_name is empty
        if log_name == "" and system_name != "":
            query["query"]["bool"]["must"].append({"match": {"system": system_name}})
        elif system_name == "" and log_name != "":
            query["query"]["bool"]["must"].append({"match": {"log": log_name}})
        elif system_name != "" and log_name != "":
            query["query"]["bool"]["must"].append({"match": {"system": system_name}})
            query["query"]["bool"]["must"].append({"match": {"log": log_name}})

        response = self.db.es.search(index=system_name, body=query)
        return response['hits']['hits']

  # mark processed flag as true
    def mark_processed(self, db, index, system_name, log_name):
        query = {
            "query": {
              "bool": {
                "must": [
                  {"match": {"system": system_name}},
                  {"match": {"log": log_name}}
                  ]
                }
              },
            "script": {
              "source": "ctx._source.details.processed = true",
              }
            }
        respone = db.es.update_by_query(index=index, body=query)
        return respone['updated']
        # TODO: maybe return other value

    def get_processed_flag(self, db, index, system_name, log_name):
        query = {
          "query": {
            "bool": {
              "must": [
                {"match": {"system": system_name}},
                {"match": {"log": log_name}}
                ]
              }
            }
          }
        response = db.es.search(index=index, body=query)
        return response['hits']['hits'][0]['_source']['details']['processed']

      # output to destination
    def output_to_destination(self, hits, db, dest_index):
        for hit in hits:
          doc = hit['_source']
          # update timestamp
          doc['details']['timestamp'] = datetime.datetime.now()
          db.insert(dest_index, doc)

if __name__ == "__main__":
  pass

