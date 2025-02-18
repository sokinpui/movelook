from langchain_google_genai import ChatGoogleGenerativeAI
import tiktoken
import yaml
import os
import random
from datetime import datetime
import es_engine
from typing import Tuple

from pydantic import BaseModel, Field
import os

_dir_path = os.path.dirname(os.path.realpath(__file__))
_config_path = os.path.join(_dir_path, 'devconfig.yml')
with open(_config_path, 'r') as f:
    _dev_config = yaml.safe_load(f)

def parsed_snapshot(snapshot : dict) -> str:
    """
    Parse the snapshot of log with line numbers
    e.g. {1: "log line 1", 2: "log line 2", ...}
    """
    log = "\n".join([f"{line_number}: {log_line}" for line_number, log_line in snapshot.items()])
    return log

def parsed_snapshot_without_line_number(snapshot : dict) -> str:
    log = "\n".join([f"{log_line}" for log_line in snapshot.values()])
    return log


class LLMBot():
    def __init__(self, config):
        self.config = self.read_config(config)
        self._es = es_engine.ESClient()
        self.__summary_index = _dev_config["llm"]['index']['summary']

        # support different models
        model = self.config["llm"]['model']
        if "gemini" in model:
            # user should define the api key inthe environment variable
            api_key = os.environ['GENAI_API_KEY']
            if api_key is None:
                raise ValueError("Please define GENAI_API_KEY in the environment variable")
            os.environ["GOOGLE_API_KEY"] = api_key
            self.llm = ChatGoogleGenerativeAI(model=model)

    def read_config(self, config_path):
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config

    def count_tokens(self, prompt):
        # approximate token count, this is used by GPT-4
        tokenizer = tiktoken.get_encoding("cl100k_base")

        tokens = tokenizer.encode(prompt)
        token_count = len(tokens)
        return token_count


    def generate(self, prompt, schema):
        """
        schema: pydantic model to structure output
        e.g.
        class Person(BaseModel):
                explanation: str = Field(description: xxx)
                linesNumber: list[int] = Field(description: xxx)
        """
        if schema:
            llm = self.llm.with_structured_output(schema)
            response = llm.invoke(prompt)
            return response
        response = self.llm.invoke(prompt)
        return response

    def summarize_files(self):
        """
        Summarize the collect files,
        get a snapshot of the log files for summarization should be enough
        insert the summarized information of the files back to Database
        """
        files = self._es.get_files()

        for file in files:

            snapshot = self._es.get_file_snapshot(
                # snapshot_size=_dev_config['llm']['snapshot_size'],
                snapshot_size=500,
                earliest_timestamp=datetime(2022, 1, 1),
                file_name=file,
                index_name=_dev_config['collector']['index']
            )

            # pass the log with line numbers to the model
            log = parsed_snapshot_without_line_number(snapshot)

            with open("./prompt/summarize_file.txt", "r") as f:
                prompt = f.read()

            prompt = prompt.replace("{filename}", file)
            prompt = prompt + "\n" + log


            response = self.generate(prompt, None)
            summary = response.content

            print(f"file: {file}")
            print(f"summary: {summary}\n")

            # isnert the response back to the database
            es = self._es.get_instance()
            body = {
                "summary": summary,
                "path": file,
                'timestamp': datetime.now(),
            }
            try:
                update_body = {
                    "doc": {
                        "summary": summary,  # New summary value
                        "path": file,  # New path value
                        "timestamp": datetime.now()  # Updated timestamp
                    },
                    "doc_as_upsert": True  # Create the document if it doesn't exist
                }
                es.update(index=self.__summary_index, id=file, body=update_body)
            except Exception as e:
                print(f"Error: {e}")
                es.index(index=self.__summary_index, body=body)

    def filter_related_files(self, files: list, event: str):
        """
        Filter the files that are related to the potential issues
        """
        # get each file's summary

        summary = {}
        related_files = []

        es = self._es.get_instance()

        for file in files:
            query = {
                    "query": {
                        "match": {
                            "path": file
                        }
                    },
            }
            response = es.search(index=self.__summary_index, body=query)

            if response['hits']['total']['value'] > 0:
                summary[file] = response['hits']['hits'][0]['_source']['summary']

        # use the model to filter the related files, give a structured output
        # define the schema
        class RelatedFiles(BaseModel):
            relatedFiles: list[str] = Field(description="list of files that are required for the event")
            explanation: str = Field(description="explain why the files are related to the event")

        with open("./prompt/filter_related_files.txt", "r") as f:
            prompt = f.read()

        prompt = prompt.replace("{event}", event)

        # convert the summary to string with format file: summary
        log_and_summary = "\n".join([f"{file}: {summary}" for file, summary in summary.items()])
        prompt = prompt.replace("{log_and_summary}", log_and_summary)

        response = self.generate(prompt, RelatedFiles)

        print(f"length: {len(response.relatedFiles)}, explanation: {response.explanation}")

        return response.relatedFiles

    def analyze_files(self, files: list):
        """
        Analyze the log files and generate the potential issues
        """
        pass

def main():
    import json
    config_path = "../config.yml"
    es = es_engine.ESClient()
    bot = LLMBot(config_path)

    # bot.summarize_files()

    files = es.get_files()

    print(files)

    with open("./prompt/events.txt", "r") as f:
        events = f.readlines()
        events = [event.strip() for event in events]
        # remove empty lines
        events = [event for event in events if event]

    from eventsGraph import EventGraph
    graph = EventGraph()
    for event in events:
        graph.add_event(event)
        related_files = bot.filter_related_files(files, event)
        graph.add_file(event, related_files)

    # print graph
    for event, files in graph.graph.items():
        print(f"event: {event}")
        print(f"length: {len(files)}")
        print(f"files: {files}\n")

    pass

if __name__ == "__main__":
    main()
