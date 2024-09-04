import yaml

class Config:
    def __init__(self, config_file):
        with open(config_file, 'r') as stream:
            self.config = yaml.safe_load(stream)

    def get_all(self):
      return self.config

    def get_reader_config(self):
      return self.config['reader']

    def get_search_items(self):
      return self.config['searchor']['systems']

    def get_seaarchor(self):
      return self.config['searchor']

    def get_search_index_name(self):
      return self.config['searchor']['index_name']

    def get_db_info(self):
      return self.config['ESHost']

if __name__ == "__main__":
  print("config.py loaded")
  config = Config("config.yml")
  print(config.get_all())
