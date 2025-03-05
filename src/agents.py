from langgraph.graph import StateGraph, END, START
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from typing import TypedDict, List, Annotated
import json

from llm_model import LLMModel, GeminiModel
from event import Event
from rag_manager import RAGManager
from prompts.role import SYSTEM_PROMPT
import prompts.agents.pre_process as pap
from logger import Logger
from log_file import LogFile
from database import ElasticsearchDatabase
import config as cfg

STOP = "stop"
CONTINUE = "continue"

def add_message(left: list[str], right: str | list[str]) -> list[str]:
    if isinstance(right, str):
        return left + [right]
    return left + right

class PreProcessAgentState(TypedDict):
    working_event: Event
    message: Annotated[list[str], add_message]
    files : List[LogFile]
    apps : List[str]
    query: dict
    hits: int

class PreProcessAgent:
    def __init__(self, model: LLMModel, rag: RAGManager, db: ElasticsearchDatabase):
        self.model = model
        self._rag = rag
        self._db = db
        self._logger = Logger()

    def _list_to_indices(self, apps: List[str]) -> str:
        return ",".join(f"log_{app}" for app in apps)

    def interpre_event(self, state: PreProcessAgentState) -> PreProcessAgentState | dict | None:
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
                "message": [response.require_info],
                "apps": response.apps,
        }

    def gen_search_query(self, state: PreProcessAgentState) -> PreProcessAgentState | dict | None:

        event = state["working_event"]
        message = state["message"]
        apps = state["apps"]

        class schema(BaseModel):
            search_queries : str = Field(description=f"""
                                        The json format boolean query to search the database
                                        for log entries related to the provided event.
                                        """)

        sample = []
        indices = self._list_to_indices(apps)

        # get random sample from the database
        random_data = self._db.random_sample(indices, cfg.RANDOM_SAMPLE_SIZE)
        for data in random_data:
            sample.append(data["_source"]["content"])

        prompt = pap.filter_logs(event.description, message, apps, sample)
        response = self.model.generate(str(sample) + prompt, schema=schema)

        query = json.loads(response.search_queries)

        return { "query": query }

    def search_in_db(self, state: PreProcessAgentState) -> PreProcessAgentState | dict | None:
        event = state["working_event"]
        query = state["query"]
        apps = state["apps"]

        indices = self._list_to_indices(apps)
        hits = self._db.add_alias(indices, f"pre_process_{event.id}", filter=query["query"])

        return { "hits": hits }

    def search_feedback(self, state: PreProcessAgentState) -> PreProcessAgentState | dict | None:
        hits = state["hits"]
        query = state["query"]
        apps = state["apps"]
        message = state["message"]

        indices = self._list_to_indices(apps)

        total_lines = self._db.count_docs(indices)

        prompt = pap.search_feedback_prompt(hits, total_lines, query, message)
        prompt = self._rag.retrieve(prompt)

        response = self.model.generate(prompt)

        return { "message": response }

def test():
    apps = ["app1", "app2"]
    indices = ",".join(f"log_{app}" for app in apps)
    print(f"indices: {indices}")
    pass

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

    e1 = Event(description="Is IP address 185.165.29.69 keep attempting to login as Invalid user via ssh")
    print(f"Event to trace: {e1.description}")

    agent = PreProcessAgent(model=model, rag=sys_info, db=es_db)

    state = {
        "working_event": e1,
        "files": collector.collected_files,
    }

    builder = StateGraph(PreProcessAgentState)
    builder.add_node("node1", agent.interpre_event)
    builder.add_node("node2", agent.gen_search_query)
    builder.add_node("node3", agent.search_in_db)
    builder.add_node("node4", agent.search_feedback)

    builder.add_edge(START, "node1")
    builder.add_edge("node1", "node2")
    builder.add_edge("node2", "node3")
    builder.add_edge("node3", "node4")
    builder.add_edge("node4", END)


    graph = builder.compile()

    result = graph.invoke(state)

    import pprint
    result["files"] = None
    pprint.pprint(result)
    print(f"len of message: {len(result['message'])}")

if __name__ == "__main__":
    # test()
    main()
