from ollama import chat, ChatResponse, generate
import ollama
import yaml
import os
import time
import resource
from datetime import datetime

print("Start time: ", datetime.now())

# Start time tracking
start_time = time.time()

def test_llm(model, prompt, options):
    response : ChatResponse = generate(model=model, prompt=prompt, options=options, stream=False)
    print(response['response'])

# import file in parent directory
with open("../log/OpenSSH_2k.log", "r") as f:
    text = ""
    # import top 10% only
    for line in f:
        text += line
        if len(text) > 1000:
            break

question = "I will prove you some logs sample, can you generate a regex pattern for me to detect potential error"
prompt = f'**question:**\n{question}\n**text source:**{text}\n'

model = "llama3.2:3b"
# options = {
#     "temperature": 0.1,
#     "top_p": 0.8,
#     "top_k": 20,
# }
options = {}
test_llm(model, prompt, options)

print()
end_time = time.time()

# Calculate time taken
execution_time = end_time - start_time

# Get memory usage
memory_usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss  # in kilobytes
memory_usage_mb = memory_usage / 1024  # Convert to megabytes
memory_usage_gb = memory_usage_mb / 1024  # Convert to megabytes

# Print results
print('Execution Time =', execution_time, 'seconds')
print('Peak Memory Usage =', memory_usage_gb, 'GB')
print("=========================================")
print()
