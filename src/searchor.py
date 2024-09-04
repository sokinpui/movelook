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

class ESSearcher:
  def __init__(self, search_items, dest_index, read_log_db, ouput_db):
    """
    search_items: search items in config.yml['searchor']['systems']
    dest_index: destination index config.yml['searchor']['indexName']
    read_log_db: the database to read from
    ouput_log_db: the database to write
    """
    # NOTE: read_log_db and output_log_db are the same
    self.search_items = search_items
    self.input_db = read_log_db
    self.output_db = ouput_db
    self.dest_index = dest_index

  # get search string
  def __get_search_string(self, system_name, system_log):
    return self.search_items[system_name][system_log]['pattern']

  def search(self ):
    for system_name in self.search_items:
      for system_log in self.search_items[system_name]:
        for string in self.search_items[system_name][system_log]:
          if self.get_processed_flag(self.input_db,system_name, system_name, system_log):
            continue
          hits = self.regex_search(string, system_name, system_log)
          self.mark_processed(self.input_db, system_name, system_name, system_log)
          self.output_to_destination(hits, self.output_db, self.dest_index)
          print(f"Search {system_name} {system_log} with {string} done")
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

    response = self.input_db.es.search(index=system_name, body=query)
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

