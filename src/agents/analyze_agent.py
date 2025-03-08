from langgraph.graph import StateGraph, END, START
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from typing import TypedDict, List, Annotated
import json

from .agent_abc import Agent, add_string_message
from event import Event
from database import ElasticsearchDatabase
from llm_model import LLMModel
from logger import Logger
import config as cfg

class AnalyzeAgentState(TypedDict):
    working_event: Event
    message: Annotated[list[str], add_string_message]
    start: int # start index of the chunk
    working_file_ids: list[str] # list of file ids

class AnalyzeAgent(Agent):
    def __init__(self, model : LLMModel, db : ElasticsearchDatabase,
                 state_dict=AnalyzeAgentState):

        self.model = model

        self.workflow = StateGraph(state_dict)
        self._build_graph()
        # self.graph = self.workflow.compile()

        self._db = db
        self._logger = Logger()

    def run(self, state: AnalyzeAgentState) -> AnalyzeAgentState:
        """
        run the agent synchronously with `invoke` method
        """
        state = self.graph.invoke(state)
        return state

    async def arun(self, state: AnalyzeAgentState) -> AnalyzeAgentState:
        """
        run the agent asynchronously with `invoke` method
        """
        state = await self.graph.ainvoke(state)
        return state

    def _build_graph(self):
        pass

    def next_chunk(self, state: AnalyzeAgentState):
        """
        Get the next chunk of text to analyze
        """
        pass

    def chunk_embedding(self, state: AnalyzeAgentState):
        """
        Embed the chunk of text
        """
        pass

    def chunk_analysis(self, state: AnalyzeAgentState):
        """
        Analyze the chunk of text
        """
        pass

    def result_memorize(self, state: AnalyzeAgentState):
        """
        Memorize the result
        """
        pass

    def _recall_memory(self, state: AnalyzeAgentState):
        """
        Recall the memory
        """
        pass

    def _get_context(self, state: AnalyzeAgentState):
        """
        Get the context from RAG
        """
        pass

    def _get_working_files(self, state: AnalyzeAgentState):
        """
        _get_working_file:
            get all the files ids from the database
        return a list of files ids
        """
        event = state["working_event"]
        ids = self._db.get_unique_values(index=cfg.get_pre_process_index(event.id), field="id")

        return {
            "working_file_ids": ids
        }


def main():
    from llm_model import GeminiModel
    db = ElasticsearchDatabase()
    model = GeminiModel()
    agent = AnalyzeAgent(model, db)

    state = {
        "working_event": Event("asdfasdfsd"),
    }

    print(db.get_unique_values_composite(index="log*", field="id"))

if __name__ == "__main__":
    main()
