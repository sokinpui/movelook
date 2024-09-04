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
from utils.repeatTimer import Timer

class Scanner:
  def __init__(self, scanner_config, db):
    """
    scanner_config = config['scanner']
    """
    self.systems = scanner_config['systems']
    self.interval = scanner_config['interval']
    self.index = scanner_config['index']
    self.db = db

  def start(self):
    self.timer = Timer(self.interval, self.search)
    self.timer.start()

  def stop(self):
    self.timer.stop()

  def search(self ):
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
  def output_to_destination(self, hits, dest_db, dest_index):
    for hit in hits:
      doc = hit['_source']
      # update timestamp
      doc['details']['timestamp'] = datetime.datetime.now()
      dest_db.insert(dest_index, doc)

if __name__ == "__main__":
  pass

