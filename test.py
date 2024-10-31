import yaml
import pprint

def load_config(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

config = load_config('config.yml')
queries = config['insightEngine']


# remove a key from dict

queries.pop('interval', None)

def __handle_operation(search_query, op):
    # concatate the pattern with "and"
    return f' {op} '.join(p for p in search_query['patterns'])

def __parser(queries):
    doc = {}
    for insight_name, search_query in queries.items():
        print(search_query)
        if 'operation' in search_query:
            if search_query['operation'] == 'and':
                # append to the doc with the key as the insight name
                doc[insight_name] = __handle_operation(search_query, "and")
        else:
            doc[insight_name] = __handle_operation(search_query, "or")
    return doc



# for insight_name, search_query in queries.items():
#     for pattern in search_query['patterns']:
#         print(pattern)

pprint.pprint(__parser(queries))
