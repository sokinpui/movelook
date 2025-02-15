import yaml
import os
import random
from datetime import datetime
from es_engine import ESClient
from analyzer import Analyzer
import llm_gemini
import json

from pydantic import BaseModel, TypeAdapter
# import google.generativeai as genai
from google import genai

dir_path = os.path.dirname(os.path.realpath(__file__))
config_path = os.path.join(dir_path, 'devconfig.yml')
with open(config_path, 'r') as f:
    devconfig = yaml.safe_load(f)

snapshot_check_prompt = f"""
Given the follow log, please check if there contains any potential issues.

You should give a explanation of the potential issues and the line numbers related to this issue.
don't give any line number within the explanation.
only return line number if you think this line is related to the potential issues.
if you think there is no potential issues, don't return any line number.

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

def get_list_of_files() -> list:
    es = ESClient().get_instance()
    query = {
        "size": 0,
        "aggs": {
            "files": {
                "terms": {
                    "field": "path.keyword",
                    "size": 1000
                }
            }
        }
    }

    response = es.search(index=devconfig['collector']['index'], body=query)
    files = [bucket['key'] for bucket in response['aggregations']['files']['buckets']]
    return files

class LLM_analyzer(Analyzer):
    def __init__(self, config):
        super().__init__(config)

    def count_tokens(self, model, prompt):
        if model == "gemini":
            return llm_gemini.count_tokens(prompt)

    def generate(self, model, prompt):
        if model == "gemini":
            return llm_gemini.generate_response(prompt)

def test(prompt):
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
    response = llm_gemini.generate_response(prompt)
    print(response)

    # insert reponse to files
    with open("response.txt", "w") as f:
        f.write(response)
    # Load the configuration

if __name__ == "__main__":
    # test(snapshot_check_prompt)

    # prompt = f"""
    # please provide me a list of potential issues that generally lookup by log analysis for cluter system log
    # """
    # response = llm_gemini.generate_response(prompt, config={})
    # print(response)

    list_of_files = get_list_of_files()
    print(list_of_files)

    # get the json files
    with open("./lookup_questions.json", "r") as f:
        lookup_aspects = f.readlines()

    class Recipe1(BaseModel):
        files: list[str]

    gemini_response_config = {
        'response_mime_type': 'application/json',
        'response_schema': Recipe1,
    }

    for aspect in lookup_aspects:
        prompt = f"""
        if I want to analysis {aspect},

        for the following files:
        {list_of_files}

        please provide me a list of files that highly related to {aspect}
        """
        response = llm_gemini.generate_response(prompt, config=gemini_response_config)
        print(f"Aspect: {aspect}")
        print(response)


