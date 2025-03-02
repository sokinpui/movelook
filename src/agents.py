from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field
from typing import TypedDict, List, Optional, Dict
import os

from llm_model import LLMModel, GeminiModel
from event import Event
from log_file import LogFile
import prompts

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

        return state

    def select_files(self, state: AgentState) -> AgentState | None:


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
