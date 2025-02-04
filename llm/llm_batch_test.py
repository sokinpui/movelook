import random
import os
import sys
import ollama
import time
import json


sample_size = 100
directory = 'logs'

# ===========llm parameters==============
options = None

prompt = "They are sample data from system log. Is there any unusual pattern? Return all the lines you think are unusual. Responsd using JSON"

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

model = "llama3.1:8b-instruct-fp16"
# model = "llama3.2:3b"
# ======================================

def init_ollama():
    # pull model llama3.1:8b
    try:
        ollama.pull(model)
    except Exception as e:
        print(f"Error pulling model: {e}")

def llm_gen(model, prompt, options, format):
    response = ollama.generate(model=model, format=format, prompt=prompt, options=options, stream=False)
    return response

def main(directory):
    # remove output file
    try:
        os.remove('output.json')
    except FileNotFoundError:
        pass
    for root, dirs, files in os.walk(directory):
        record = {}
        for log in files:
            text = random_lines_from_file(log, root)
            text = f"{text}\n\n"
            question = text + prompt
            start = time.time()
            response = llm_gen(model, question, options, format)
            end = time.time()
            # record['response'] = response['response']
            record[log] = {
                    "duration": f"{end - start:.10}s",
                    "response": response['response']
            }
        with open('output.json', 'a') as f:
            json.dump(record, f, indent=4)

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
init_ollama()
main(directory)
