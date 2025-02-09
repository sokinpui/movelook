import random
from datetime import datetime
from es_engine import ESClient

def get_file_snapshot(snapshot_size: int, earliest_timestamp: datetime, file_name : str,  index_name: str):
    es = ESClient().get_instance()

    # Initial query with scroll enabled to fetch all logs after earliest_timestamp
    # make es field configurable
    query = {
        "size": 1000,  # Fetch in chunks
        "query": {
            "bool": {
                "must": [
                    {"range": {"timestamp": {"gt": earliest_timestamp.strftime("%Y-%m-%dT%H:%M:%S")}}},
                    {"match": {"path": file_name}}  # Filter by file name (assuming 'path' stores file name)
                ]
            }
        },
        "sort": [{"lineNumber": "asc"}]  # Sort by line number instead of timestamp
    }

    # Start scrolling
    response = es.search(index=index_name, body=query, scroll="2m")
    scroll_id = response["_scroll_id"]
    hits = response["hits"]["hits"]

    log_data = []

    # Keep scrolling until no more results
    while hits:
        log_data.extend([
            {"line_number": hit["_source"]["lineNumber"], "content": hit["_source"]["line"]}
            for hit in hits
        ])
        response = es.scroll(scroll_id=scroll_id, scroll="2m")  # Fetch next batch
        scroll_id = response["_scroll_id"]
        hits = response["hits"]["hits"]

    # Clear the scroll context in Elasticsearch
    es.clear_scroll(scroll_id=scroll_id)

    # If there's not enough data, return all available logs
    if len(log_data) <= snapshot_size:
        return log_data

    # Select a random continuous subset
    start_index = random.randint(0, len(log_data) - snapshot_size)
    return log_data[start_index:start_index + snapshot_size]


