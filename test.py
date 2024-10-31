import yaml
import pprint

def load_config(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

config = load_config('config.yml')
queries = config['insight']


# remove a key from dict

queries.pop('interval', None)

def __handle_operation(search_query, op):
    # Extract patterns from the search query
    patterns = search_query.get('patterns', [])

    # Initialize the Elasticsearch query
    if op == "and":
        # Use a 'must' clause for 'and' operation (all patterns must match)
        query = {
            "bool": {
                "must": []
            }
        }
        for pattern in patterns:
            query["bool"]["must"].append({
                "regex": {
                    "field_name": pattern  # Replace 'field_name' with the actual field you want to search
                }
            })
    else:
        # Use a 'should' clause for 'or' operation (any pattern can regex)
        query = {
            "bool": {
                "should": []
            }
        }
        for pattern in patterns:
            query["bool"]["should"].append({
                "regex": {
                    "field_name": pattern  # Replace 'field_name' with the actual field you want to search
                }
            })

    return query

def __parser_to_doc(queries):
    doc = {}
    for insight_group, search_query in queries.items():
        print(search_query)
        if 'operation' in search_query:
            if search_query['operation'] == 'and':
                # append to the doc with the key as the insight name
                doc[insight_group] = __handle_operation(search_query, "and")
            elif search_query['operation'] == 'or':
                # append to the doc with the key as the insight name
                doc[insight_group] = __handle_operation(search_query, "or")
        else:
            doc[insight_group] = __handle_operation(search_query, "or")
    return doc

result = __parser_to_doc(queries)
pprint.pprint(result)
