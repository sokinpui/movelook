import random
from datetime import datetime
from es_engine import ESClient
import os
import yaml
from pydantic import BaseModel, TypeAdapter
# import google.generativeai as genai
from google import genai
from llms import get_file_snapshot

class Recipe(BaseModel):
    explanation: str
    linesNumber: list[int]

api_key = os.environ['GENAI_API_KEY']

def count_tokens(prompt):
    contents = prompt
    model="gemini-1.5-flash-8b"
    client = genai.Client(api_key=api_key)
    response = client.models.count_tokens(
        model=model,
        contents=contents,
     )
    return response.total_tokens

gemini_response_config = {
    'response_mime_type': 'application/json',
    'response_schema': Recipe,
}

def generate_response(prompt, config=gemini_response_config):
    contents = prompt
    model="gemini-1.5-flash-8b"
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=config
     )
    return response.text

if __name__ == "__main__":
    dir_path = os.path.dirname(os.path.realpath(__file__))
    config_path = os.path.join(dir_path, 'devconfig.yml')
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    files = "OpenSSH_2K.log"
    snapshot = get_file_snapshot(
        snapshot_size=1000,
        earliest_timestamp=datetime(2022, 1, 1),
        file_name=files,
        index_name=config['collector']['index']
    )
    # print the range of line number in snapshot
    print(f"Line number range: {min(snapshot.keys())} - {max(snapshot.keys())}")

    # generate prompt: lineNumber: logLine
    log = "\n".join([f"{line_number}: {log_line}" for line_number, log_line in snapshot.items()])
    prompt = f"""
    Given the follow log, please check if there contains any potential issues.
    You should give a explanation of the potential issues and the line number of the log.
    don't give any line number within the explanation.

    log structure: lineNumber: logLine

    Log content:
    {log}
    """
    token_count = count_tokens(prompt)
    print(f"Token count: {token_count}")
    response = generate_response(prompt)
    print(response)
