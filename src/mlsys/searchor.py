from utils.database import Database

class Search:
  def __init__(self, search_items):
    self.search_items = search_items
    self.es = Database()

  # get search string
  def get_search_string(self, system_name, system_log):
    return self.search_items[system_name][system_log]['pattern']

  def search(self):
    for system_name in self.search_items:
      for system_log in self.search_items[system_name]:
        search_string = self.get_search_string(system_name, system_log)

  # to check whether field is being processed
  def is_processed(self):
    pass

  # mark processed flag as true
  def mark_processed(self):
    pass

  # output searched results
  def output(self):
    pass

if __name__ == "__main__":
  import rconfig
  config = rconfig.Config("config.yml")

