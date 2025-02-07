import random
import os
import sys
# import ollama
import time
import json
from datetime import datetime

from pydantic import BaseModel, TypeAdapter
# import google.generativeai as genai
from google import genai


# read as sys.args
sample_size = int(sys.argv[1])
directory = 'logs'

# ===========llm parameters==============
options = None

# llama
# prompt = "They are sample data from system log. Is there any unusual pattern? Return all the lines you think are unusual. Responsd using JSON"

# gemini
prompt = "They are sample data from system log. Is there any unusual pattern? Return all the lines you think are unusual."

prompt = prompt + "If you think there is no unusual pattern, do not return any lines."

# format of the response
format = {
    "type": "object",
    "properties": {
        "explanation": {
            "type": "string",
            },
        "lines":{
            "type": "array",
            "items": {
                "type": "string"
                }
            }
        },
    "required": [
        "explanation",
        "lines"
    ]
}

model = "llama3.1:8b-instruct-q4_K_M"
# model = "llama3.1:8b-instruct-fp16"
# model = "llama3.2:3b"
# ======================================
# save runnig iteration to a file
with open('iteration.txt', 'r') as f:
    i = int(f.read())

output_file = f"output_{i}.json"

def init_ollama():
    # pull model llama3.1:8b
    try:
        ollama.pull(model)
    except Exception as e:
        print(f"Error pulling model: {e}")

def llama_gen(model, prompt, options, format):
    response = ollama.generate(model=model, format=format, prompt=prompt, options=options, stream=False)
    return response

class Recipe(BaseModel):
    explanation: str
    lines: list[str]

def gemini_count_tokens(prompt):
    contents = prompt
    model="gemini-1.5-flash-8b"
    client = genai.Client(api_key="AIzaSyAl3zXcN2s_UVe3lnfJAA38iORw5dYAgJw")
    response = client.models.count_tokens(
        model=model,
        contents=contents,
     )
    return response


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

def main(directory):
    # remove output file
    program_start = time.time()
    for root, dirs, files in os.walk(directory):
        record = {}
        record["sample_size"] = sample_size
        for log in files:
            print(f"Processing {log}")
            text = random_lines_from_file(log, root)
            text = f"{text}\n\n"
            question = text + prompt
            start = time.time()
            print(f"start time: {datetime.now()}")

            # count tokens
            total_tokens = gemini_count_tokens(question)
            print(f"Total tokens: {total_tokens.total_tokens}")

            # generate response from gemini
            try:
                response = gemini_gen(question)
            except Exception as e:
                print(f"Error generating response: {e}")
                continue

            # generate response from llama
            # response = llama_gen(model, question, options, format)
            end = time.time()
            print(f"duration: {end - start}")
            # record['response'] = response['response']
            record[log] = {
                    "total_tokens": total_tokens.total_tokens,
                    "duration": f"{end - start:.10}s",
                    "response": response
            }
        with open(f'output/{output_file}', 'a') as f:
            json.dump(record, f, indent=4)

        # update iteration number
        with open('iteration.txt', 'w') as f:
            f.write(str(i + 1))

        print()
        print("=====================================")
        program_end = time.time()
        total_lines_processed = len(files) * sample_size
        print(f"Total time: {(program_end - program_start)/60:.4f}min")
        print(f"Total lines processed: {total_lines_processed}")

def random_lines_from_file(log, root):
    log_path = os.path.join(root, log)
    with open(log_path, 'r') as f:
        # 100 randon lines
        files = f.readlines()
        min_sample_size = min(sample_size, len(files))
        random_lines = random.sample(files, min_sample_size)
        text = ""
        for line in random_lines:
            text += repr(line)
        return text

# res = llm_gen(model, prompt, options, format)
# start ollama first
# init_ollama()
main(directory)
