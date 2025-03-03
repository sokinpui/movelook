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
from log_file import LogFile

STOP = "stop"
CONTINUE = "continue"

class PreProcessAgentState(TypedDict):
    working_event: Event
    message: str
    files : List[LogFile]
    apps : List[str]

class PreProcessAgent:
    def __init__(self, model: LLMModel, rag: RAGManager):
        self.model = model
        self._rag = rag
        self._logger = Logger()

    def interpre_event(self, state: PreProcessAgentState) -> PreProcessAgentState | dict | None:
        self._logger.info(f"agents: {self.__class__.__name__}.interpre_event:")
        event = state["working_event"]
        files = state["files"]

        prompt = pap.interpre_event_prompt(event.description, files)
        retrieved_prompt = self._rag.retrieve(prompt)

        class schema(BaseModel):
            require_info : str = Field(description=f"""
                                       require information to trace the event from the log,
                                       and the applications that are relevant to the event.
                                       """)
            apps : List[str] = Field(description=f"""
                                    list of applications inside the system as mentioned,
                                    that are related and required to trace the event.
                                    """)

        response = self.model.generate(SYSTEM_PROMPT + retrieved_prompt, schema=schema)

        print(f"require_info: {response.require_info}")
        print(f"apps: {response.apps}")

        return {
                "message": response.require_info,
                "apps": response.apps,
        }

    def filter_logs_lines(self, state: PreProcessAgentState) -> PreProcessAgentState | dict | None:
        self._logger.info(f"agents: {self.__class__.__name__}.filter_logs_lines:")

        event = state["working_event"]
        message = state["message"]
        apps = state["apps"]

        prompt = pap.filter_logs(event.description, message, apps)
        retrieved_prompt = self._rag.retrieve(prompt)

        class schema(BaseModel):
            search_queries : str = Field(description=f"""
                                                the search queries to fileter the logs based on the event
                                                """)

        response = self.model.generate(SYSTEM_PROMPT + retrieved_prompt, schema=schema)
        import json
        queries = json.loads(response.search_queries)

        print(f"search_queries:\n{json.dumps(queries, indent=4)}")

        return

def test():
    from new_collector import NewCollector

    dir = "../log"
    collector = NewCollector(dir=dir)
    files = collector.collected_files

    event = "The system is down"

    info = "failed login attempts, authentication failures, invalid user attempts, brute-force attacks, and relevant timestamps"

    apps = ["ssh"]

    print(pap.filter_logs(event, info, apps))



def main():
    from llm_model import GeminiModel
    from database import ElasticsearchDatabase
    from new_collector import NewCollector

    model = GeminiModel()
    es_db = ElasticsearchDatabase()
    collector = NewCollector(dir="../log")

    # create rag manager
    embeddings = model.embedding
    sys_info = RAGManager(name="systme_los_info_overview", db=es_db, embeddings=embeddings, model=model)

    # sys_info.update_rag_from_directory("../rag/docs/", es_db)

    e1 = Event(description="want to find if there is any high frequency of failed login attempts using ssh")
    print(f"Event to trace: {e1.description}")

    agent = PreProcessAgent(model=model, rag=sys_info)

    state = {
        "working_event": e1,
        "files": collector.collected_files,
    }

    builder = StateGraph(PreProcessAgentState)
    builder.add_node("start", agent.interpre_event)
    builder.add_node("filter_logs_lines", agent.filter_logs_lines)
    builder.set_entry_point("start")

    builder.add_edge("start", "filter_logs_lines")

    graph = builder.compile()

    result = graph.invoke(state)

if __name__ == "__main__":
    main()
