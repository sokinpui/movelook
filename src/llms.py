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

_snapshot_check_prompt = f"""
Given the follow log, please check if there contains any potential issues.

You should give a very detail explanation of the potential issues and the line numbers related to this issue.
don't give any line number within the explanation.
only return line number if you think this line is related to the potential issues.
if you think there is no potential issues, don't return any line number.

log structure: lineNumber: logLine

Log content:\n
"""

def parsed_snapshot(snapshot : dict) -> str:
    """
    Parse the snapshot of log with line numbers
    e.g. {1: "log line 1", 2: "log line 2", ...}
    """
    log = "\n".join([f"{line_number}: {log_line}" for line_number, log_line in snapshot.items()])
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
                snapshot_size=1000,
                earliest_timestamp=datetime(2022, 1, 1),
                file_name=file,
                index_name=_dev_config['collector']['index']
            )

            log = parsed_snapshot(snapshot)

            with open("./prompt/summarize_file.txt", "r") as f:
                prompt = f.read()

            # replace the placeholder inside prompt
            prompt = prompt.replace("{log}", log)
            prompt = prompt.replace("{file_name}", os.path.basename(file))

            response = self.generate(prompt, None)
            summary = response.content

            # debug print with color
            print(f"Summary for file {file}: {summary}\n")

            # isnert the response back to the database
            es = self._es.get_instance()
            body = {
                "summary": summary,
                "path": file,
                'timestamp': datetime.now(),
            }
            try:
                es.update_by_query(index=self.__summary_index, body=body)
            except Exception as e:
                es.index(index=self.__summary_index, body=body)

    def filter_related_files(self, files: list, event: str) -> Tuple[list, str]:
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
            relatedFiles: list[str] = Field(description="list of related files")
            explanation: str = Field(description="explanation of the related files")

        with open("./prompt/filter_related_files.txt", "r") as f:
            prompt = f.read()

        prompt = prompt.replace("{event}", event)
        # convert the summary to string with format file: summary
        summary = "\n".join([f"{file}: {summary}" for file, summary in summary.items()])
        prompt = prompt.replace("{summary}", str(summary))

        response = self.generate(prompt, RelatedFiles)

        return response.relatedFiles, response.explanation

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

    bot.summarize_files()

    files = es.get_files()
    print(f"Got {len(files)} files in total")

    with open("./prompt/events.txt", "r") as f:
        events = f.readlines()
        print(f"find {len(events)} events")

    related_files_to_event = {}

    for event in events:
        event = event.strip()
        related_files, explanation = bot.filter_related_files(files, event)

        related_files_to_event[event] = {
                "related_files": related_files,
                "explanation": explanation
                }

    with open("output/files_related_to_this_event.json", "w") as f:
        f.write(json.dumps(related_files_to_event, indent=4))
    pass

if __name__ == "__main__":
    main()
