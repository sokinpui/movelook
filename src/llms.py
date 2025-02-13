import yaml
import os
import random
from datetime import datetime
from es_engine import ESClient
from analyzer import Analyzer
import llm_gemini

from pydantic import BaseModel, TypeAdapter
# import google.generativeai as genai
from google import genai

dir_path = os.path.dirname(os.path.realpath(__file__))
config_path = os.path.join(dir_path, 'devconfig.yml')
with open(config_path, 'r') as f:
    devconfig = yaml.safe_load(f)

prompt = f"""
Given the follow log, please check if there contains any potential issues.

You should give a explanation of the potential issues and the line number of the log.
don't give any line number within the explanation.

log structure: lineNumber: logLine

Log content:\n
"""

def parsed_snapshot(snapshot):
    log = "\n".join([f"{line_number}: {log_line}" for line_number, log_line in snapshot.items()])
    return log

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

class LLM_analyzer(Analyzer):
    def __init__(self, config):
        super().__init__(config)

    def count_tokens(self, model, prompt):
        if model == "gemini":
            return llm_gemini.count_tokens(prompt)

    def generate(self, model, prompt):
        if model == "gemini":
            return llm_gemini.generate_response(prompt)

if __name__ == "__main__":
    config = "../config.yml"
    llm = LLM_analyzer(config)
    files = "OpenSSH_2K.log"

    snapshot = get_file_snapshot(
        snapshot_size=devconfig["analyzer"]['llm']['snapshot_size'],
        earliest_timestamp=datetime(2022, 1, 1),
        file_name=files,
        index_name=devconfig['collector']['index']
    )
    log = parsed_snapshot(snapshot)
    print(f"Line number range: {min(snapshot.keys())} - {max(snapshot.keys())}")
    prompt += log

    # use gemini model to generate response
    total_tokens = llm.count_tokens("gemini", prompt)
    print(f"Total tokens: {total_tokens}")
    response = llm_gemini.generate_response(prompt, config={})
    print(response)

    # insert reponse to files
    with open("response.txt", "w") as f:
        f.write(response)
    # Load the configuration
