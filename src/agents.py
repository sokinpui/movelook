from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field
from typing import TypedDict, List, Optional, Dict
import os

from llm_model import LLMModel, GeminiModel
from event import Event
from log_file import LogFile
import prompt.agent as pa

STOP = "stop"
CONTINUE = "continue"

class AgentState(TypedDict):
    events: List[Event]
    working_event: Event
    files: List[LogFile]
    selected_file_id: List[int] # the id of the file
    working_files: int # the id of the file
    short_term_memory: List[str] # process per files
    long_term_memory: List[str] # process per evnet
    message: str
    stop: bool

class PreprocessAgent:
    def __init__(self, model: LLMModel):
        self.model = model

    def get_next_event(self, state: AgentState) -> AgentState | None:
        state["working_event"] = state["events"].pop()

        query = f"""
        Give the following event a short name in 2 to 3 words

        event: {state["working_event"].description}
        """

        class schema(BaseModel):
            short_name: str = Field(description="short name of the event")

        response = self.model.generate(query, schema)
        state["working_event"].name = response["short_name"]

        return state

    def select_files(self, state: AgentState) -> AgentState | None:
        working_event = state["working_event"]

        analysize_prompt = f"""
        You are ask to trace the event: {working_event.name} from a system.
        what information is needed for the event: {working_event.name}?
        what application is involved?

        ## details of {working_event.name}
        {working_event.description}
        """

        response = self.model.generate(analysize_prompt)

        class schema(BaseModel):
            ids_of_files: List[int] = Field(description="id of the files to be selected")

        files =state["files"]
        files_list = "\n".join([f"{file.id}: {file.belongs_to} - {os.path.basename(file.name)}" for file in files])

        select_file_prompt = f"""
        You are tracing a event: {working_event.name} from a system.
        You have to select the files that are relevant to the event: {working_event.name}, from a given list of system logs file name.
        You need not return the file name, just return the id of the files that are relevant.

        ## useful information
        here are some useful information about the event: {working_event.name}
        {working_event.description}

        {response}

        ## list of files (id: category - file name)
        {files_list}
        """

        selection = self.model.generate(select_file_prompt, schema)
        state["selected_file_id"] = selection.ids_of_files

        return state

class AnalyzeAgent:
    def __init__(self, model: LLMModel):
        self.model = model

    def pick

def main():
    from new_collector import NewCollector
    import os

    model = GeminiModel()

    dir = "../log/"
    c = NewCollector(dir)
    files = c.collect_logs(dir)

    list_of_files = "\n".join([f"{file.id}: {file.belongs_to} - {os.path.basename(file.name)}" for file in files])

    print(list_of_files)
    pass

if __name__ == "__main__":
    main()
