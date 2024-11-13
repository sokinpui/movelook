import yaml

def load_config(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

config = load_config('config.yml')
config = config['insightEngine']

def parser(query):
    p = query['pattern']
    # if p[0] is a dict and their is a key "operation" in it:
    if isinstance(p[0], dict) and 'operation' in p[0]:
        # if operation is "and"
        if p[0]['operation'] == 'and':
            return and_operation(p)
    return ' or '.join(p for p in query['pattern'])

def and_operation(p):
    patterns = p[1:]
    # concatate the pattern with "and"
    return ' and '.join(p for p in patterns if p != 'operation')

for query in config:
    # skip if it is "interval"
    if query == 'interval':
        continue
    print(parser(config[query]))


