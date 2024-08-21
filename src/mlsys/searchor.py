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

from utils.database import Database

class ESSearcher:
  def __init__(self, search_items, read_log_db, ouput_log_db):
    self.search_items = search_items
    self.input_db = read_log_db
    self.output_db = ouput_log_db
    # TODO: support config in config.yml
    self.searcher_index = "lookup"

  # get search string
  def __get_search_string(self, system_name, system_log):
    return self.search_items[system_name][system_log]['pattern']

  # maybe this search function can change outside is more fixiable for search
  def search(self, dest_index):
    for system_name in self.search_items:
      for system_log in self.search_items[system_name]:
        search_string = self.__get_search_string(system_name, system_log)
        respone = self.regex_search(search_string, system_name, system_log)
        self.mark_processed(self.input_db, system_name, system_name, system_log)
        self.output_to_destination(self.output_db, dest_index, respone)


  def regex_search(self, search_string, system_name="", log_name=""):
    query = {
        "query": {
          "bool": {
            "must": [
              {"regexp": {"details.line": search_string}}
              ]
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

    response = self.input_db.search(index=system_name, body=query)
    return response['hits']
    # TODO: check which one is more suitable
    # return response['hits']['hits']

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
    respone = db.update_by_query(index=index, body=query)
    # TODO: maybe return other value
    return respone['hits']

  # TODO: assume write to stdout
  # output searched results
  def output(self):
    pass

  # output to destination
  def output_to_destination(self, dest_db, dest_index, query):
    dest_db.insert(dest_index, query)

if __name__ == "__main__":
  pass

