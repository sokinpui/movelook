import random
from datetime import datetime
from es_engine import ESClient
import os
import yaml
from pydantic import BaseModel, TypeAdapter
# import google.generativeai as genai
from google import genai

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
    response = es.search(
            index=index_name,
            body=query,
            scroll="2m"
            )
    scroll_id = response["_scroll_id"]
    scroll_size = len(response["hits"]["hits"])

    log_data = {}

    while scroll_size > 0:
        for hit in response["hits"]["hits"]:
            log_data[hit["_source"]["lineNumber"]] = hit["_source"]["line"]
        response = es.scroll(scroll_id=scroll_id, scroll="2m")
        scroll_id = response["_scroll_id"]
        scroll_size = len(response["hits"]["hits"])

    # Clear the scroll context in Elasticsearch
    es.clear_scroll(scroll_id=scroll_id)

    # If there's not enough data, return all available logs
    if len(log_data) <= snapshot_size:
        return log_data

    # Randomly select continue 'snapshot_size' lines from the fetched logs
    line_numbers = list(log_data.keys())
    start_index = random.randint(0, len(line_numbers) - snapshot_size)
    snapshot = {}
    for i in range(start_index, start_index + snapshot_size):
        snapshot[line_numbers[i]] = log_data[line_numbers[i]]

    return snapshot

class Recipe(BaseModel):
    explanation: str
    linesNumber: list[int]

def gemini_count_tokens(prompt):
    contents = prompt
    model="gemini-1.5-flash-8b"
    client = genai.Client(api_key="AIzaSyAl3zXcN2s_UVe3lnfJAA38iORw5dYAgJw")
    response = client.models.count_tokens(
        model=model,
        contents=contents,
     )
    return response.total_tokens


def gemini_gen(prompt):
    contents = prompt
    model="gemini-1.5-flash-8b"
    client = genai.Client(api_key="AIzaSyAl3zXcN2s_UVe3lnfJAA38iORw5dYAgJw")
    response = client.models.generate_content(
        model=model,
        contents=contents,
        config={
            'response_mime_type': 'application/json',
            'response_schema': Recipe,
        },
     )
    return response.text

if __name__ == "__main__":
    dir_path = os.path.dirname(os.path.realpath(__file__))
    config_path = os.path.join(dir_path, 'devconfig.yml')
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    files = "OpenSSH_2K.log"
    snapshot = get_file_snapshot(
        snapshot_size=1500,
        earliest_timestamp=datetime(2022, 1, 1),
        file_name=files,
        index_name=config['collector']['index']
    )
    # print the range of line number in snapshot
    print(f"Line number range: {min(snapshot.keys())} - {max(snapshot.keys())}")

    # generate prompt: lineNumber: logLine
    log = "\n".join([f"{line_number}: {log_line}" for line_number, log_line in snapshot.items()])
    prompt = f"Given the following logs each lines come with a line number indicate the location of this line in the files, is there any potential issue?Report all the line number\n{log}"
    token_count = gemini_count_tokens(prompt)
    print(f"Token count: {token_count}")
    response = gemini_gen(prompt)
    print(response)
