# read config.yml file
import yaml

with open("config.yml", 'r') as ymlfile:
    config = yaml.safe_load(ymlfile)
    print(config['systems'])


