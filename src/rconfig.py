import yaml

class Config:
    def __init__(self, config_file):
        with open(config_file, 'r') as stream:
            self.config = yaml.safe_load(stream)

    def get(self, key):
        return self.config[key]

    def get_all(self):
      return self.config

if __name__ == "__main__":
  print("config.py loaded")
  config = Config("config.yml")
  print(config.get_all())
