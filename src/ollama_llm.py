from ollama import chat, ChatResponse
import ollama
import yaml
import os

# with open("./pattern_extractor.py", "r") as f:
#     file = f.readlines()
#
# response : ChatResponse = chat(model="llama3.2:3b", messages=[
#     {
#         'role': 'user',
#         'content': f'answer either "yes" or "no"\ncontext/files/text:{file} \nquestion: is this a python file\n'
#         }
#     ])
#
# print(response['message']['content'])



def start_ollama():
    try:
        with open('config.yml', 'r') as f:
            config = yaml.safe_load(f)
            os.system("ollama serve")
            model = config["llm_model"]
            ollama.pull(model)
    except FileNotFoundError:
        print("Error: config.yml file not found.")
    except KeyError as e:
        print(f"Error: Missing key in config.yml: {e}")
    except yaml.YAMLError as exc:
        print(f"Error parsing YAML: {exc}")
    # run `ollama serve` on command line first
    except Exception as e:
        print(f"Error: {e}")



