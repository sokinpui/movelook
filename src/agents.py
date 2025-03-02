from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field
from typing import TypedDict, List, Optional, Dict
import os

from llm_model import LLMModel, GeminiModel
from event import Event
from rag_manager import RAGManager
from prompts.role import SYSTEM_PROMPT
import prompts.agents.pre_process as pap
from logger import Logger

STOP = "stop"
CONTINUE = "continue"

class PreProcessAgentState(TypedDict):
    working_event: Event
    message: str

class PreProcessAgent:
    def __init__(self, model: LLMModel, rag: RAGManager):
        self.model = model
        self._rag = rag
        self._logger = Logger()

    def interpre_event(self, state: PreProcessAgentState) -> PreProcessAgentState | dict | None:
        event = state["working_event"]

        prompt = pap.interpre_event_prompt(event.description)
        retrieved_prompt = self._rag.retrieve(prompt)
        response = self.model.generate(SYSTEM_PROMPT + retrieved_prompt)

        return { "message": response }


    def filter_logs_lines(self, state: PreProcessAgentState) -> PreProcessAgentState | dict | None:
        event = state["working_event"]
        message = state["message"]

        prompt = pap.filter_logs(event.description, message)

        retrieved_prompt = self._rag.retrieve(prompt)

        response = self.model.generate(SYSTEM_PROMPT + retrieved_prompt)

        return { "message": response }


def main():
    from llm_model import GeminiModel
    from database import ElasticsearchDatabase

    model = GeminiModel()
    es_db = ElasticsearchDatabase()

    # create rag manager
    embeddings = model.embedding
    sys_info = RAGManager(name="systme_los_info_overview", db=es_db, embeddings=embeddings, model=model)

    sys_info.update_rag_from_directory("../rag/docs/", es_db)

    e1 = Event(description="want to find if there is high frequency of failed login attempts in the system logs")
    agent = PreProcessAgent(model=model, rag=sys_info)

    state = {
        "working_event": e1,
    }

    builder = StateGraph(PreProcessAgentState)
    builder.add_node("start", agent.interpre_event)
    builder.add_node("filter_logs_lines", agent.filter_logs_lines)
    builder.set_entry_point("start")

    builder.add_edge("start", "filter_logs_lines")

    graph = builder.compile()

    result = graph.invoke(state)

    for key, value in result.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    main()
