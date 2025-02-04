from ollama import chat, ChatResponse, generate
import yaml
import os
import time
from datetime import datetime
from memory_profiler import profile
import matplotlib.pyplot as plt
import time
import json
import random



# Start time tracking
# import file in parent directory

def llm_chat(model, prompt, options, format):
    # response : ChatResponse = generate(model=model, prompt=prompt, options=options, stream=False)
    response : ChatResponse = chat(model=model,
                                   messages= [{ "role": "user", "content": prompt }],
                                   options=options,
                                   format=format,
                                   stream=False)
    print(response['message']['content'])

def llm_generate(model, prompt, options, format) -> ChatResponse:
    response : ChatResponse = generate(model=model, format=format, prompt=prompt, options=options, stream=False)
    print(response)
    return response

# prompt give to the model

def main():
    with open("../log/OpenSSH_2k.log", "r") as f:
        lines = f.readlines()

# read 50 random lines from the file
    text = ""
    # num_lines = min(100, len(lines))
    # random_lines = random.sample(lines, num_lines)
    random_lines = lines[:100]
    for line in random_lines:
        text += repr(line)

    incidents = "Login Attempts with Disabled Accounts"
    # question = f"You are a regex pattern generator. Learn from the following sample data and generate a regex pattern that can identify the incidents from the original log:{incidents}. Responsd using JSON"

    question = "is there any invalid user try to login? return all lines related."

    prompt = f'{text}\n\n{question}'

# model and model options/parrameters
    model = "llama3.2:3b-text-q8_0"
    # options = {
    #     "temperature": 0,
    # }
    options = None

# format of the response
    # format = {
    #         "type": "object",
    #         "properties": {
    #             "regex_pattern": {
    #                 "type": "string",
    #                 }
    #             },
    #         "required": ["regex_pattern"]
    #         }
    format = None

    text = ""

    print("Start time: ", datetime.now())
    print()

    print("===================response====================")
    start_time = time.time()

    res = llm_generate(model, prompt, options, format)

    # json_string = res['response']
    # json_dict = json.loads(json_string)
    # print(json_dict['regex_pattern'])
    #
    # regex_pattern = json_dict['regex_pattern']
    #
    end_time = time.time()
    print(f"Execution time: {end_time - start_time:.4f} seconds")

    # return regex_pattern


if __name__ == "__main__":
    main()
    pass
