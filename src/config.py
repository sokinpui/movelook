import yaml

class Config:
    def __init__(self, config_file):
        with open(config_file, 'r') as stream:
            self.config = yaml.safe_load(stream)

    def get_all_config(self):
      return self.config

    def get_collector_config(self):
      return self.config['collector']

    def get_scanner_config(self):
      return self.config['scanner']

    def get_database_config(self):
      return self.config['database']

if __name__ == "__main__":
  print("config.py loaded")
  config = Config("config.yml")
  print(config.get_all_config())
