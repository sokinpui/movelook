# validate config file, raise error if not validate

import os
import yaml
import re

default_config_path = '$HOME/.config/ml/config.yml'

def validate_name(name):
    # Check length
    if len(name) > 255:
        raise ValueError("Name cannot be longer than 255 characters.")

    # Check for invalid characters
    invalid_chars = r'[\\/*?"<>|,#:;[\]{}!@#$%^&()]'
    if re.search(invalid_chars, name):
        raise ValueError("Name cannot include invalid characters: \\ / * ? \" < > | , # : ; ] [ } { ! @ # $ % ^ & ()")

    # Check if name starts with -, _, or +
    if name.startswith(('-', '_', '+')):
        raise ValueError("Name cannot start with '-', '_', or '+'.")

    # Check if name is '.' or '..'
    if name in ('.', '..'):
        raise ValueError("Name cannot be '.' or '..'.")


def validate_config(config):
    required_keys = ['database', 'collector', 'patterns', 'actions']

    for key in required_keys:
        if key not in config:
            raise KeyError(f"Missing required section: {key}")

    # Validate database section
    db = config['database']
    if not isinstance(db, dict) or 'host' not in db:
        raise KeyError("Missing or invalid 'host' in database configuration.")

    host = db['host']
    if not all(k in host for k in ['scheme', 'host', 'port']):
        raise KeyError("Missing required fields in database host configuration.")

    # Validate collector section
    if 'directory' not in config['collector']:
        raise KeyError("Missing 'directory' in collector configuration.")

    # Validate patterns section
    patterns = config['patterns']
    if 'regex' not in patterns or not isinstance(patterns['regex'], list):
        raise KeyError("Missing or invalid 'regex' patterns configuration.")

    for pattern in patterns['regex']:
        if not all(k in pattern for k in ['name', 'pattern', 'action']):
            raise KeyError("Missing required fields in pattern configuration.")

    # check if the name of the pattern is validate
    names = [pattern['name'] for pattern in patterns['regex']]
    for name in names:
        validate_name(name)

    # Validate actions section
    # actions = config['actions']
    # for action in patterns['regex']:
    #     if action['action'] not in actions:
    #         raise KeyError(f"Undefined action: {action['action']}")


def config_checker():
    if not os.path.isfile(default_config_path):
        raise FileNotFoundError(f"Config file not found at: {default_config_path}")

# load and parse yaml
    with open(default_config_path, 'r') as file:
        try:
            config = yaml.safe_load(file)
        except yaml.YAMLError as exc:
            raise ValueError(f"Error parsing YAML file: {exc}")

    validate_config(config)
    return config
