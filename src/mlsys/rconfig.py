import yaml

class Config:
    def __init__(self, config_file):
        with open(config_file, 'r') as stream:
            self.config = yaml.safe_load(stream)

    def get_all(self):
      return self.config

    def get_search_items(self):
      return self.config['searchPattern']['systems']

if __name__ == "__main__":
  print("config.py loaded")
  config = Config("config.yml")
  print(config.get_all())
