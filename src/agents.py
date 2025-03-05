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
    route_back: bool

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

        self._logger.info(f"Agent: Event: {event.description[:50]}... | Apps: {', '.join(response.apps)}")

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

        try:
            query = json.loads(response.search_queries)
            self._logger.info(f"Agent: search query successfully generated")
        except json.JSONDecodeError as e:
            self._logger.error(f"error in decoding the search query: {e}")
            return { "query": None }

        return { "query": query }

    def search_in_db(self, state: PreProcessAgentState) -> PreProcessAgentState | dict | None:
        event = state["working_event"]
        query = state["query"]
        apps = state["apps"]

        indices = self._list_to_indices(apps)
        hits = self._db.add_alias(indices, f"pre_process_{event.id}", filter=query["query"])

        self._logger.info(f"Agent: DB Search: {hits} hits | Event ID: {event.id}")

        return { "hits": hits }

    def search_feedback(self, state: PreProcessAgentState) -> PreProcessAgentState | dict | None:
        hits = state["hits"]
        query = state["query"]
        apps = state["apps"]
        message = state["message"]
        event = state["working_event"]

        indices = self._list_to_indices(apps)

        total_lines = self._db.count_docs(indices)

        prompt = pap.search_feedback_prompt(hits, total_lines, query, event, message)
        prompt = self._rag.retrieve(prompt)

        class schema(BaseModel):
            message : str = Field(description=f"your feedback on the search results")
            route_back : bool = Field(description=f"True if hits is out of range, False otherwise")

        response = self.model.generate(prompt, schema=schema)

        self._logger.info(f"Agent:Feedback: route_back={response.route_back} | hits rate={hits/total_lines:.2f}%")

        return {
            "message": [response.message],
            "route_back": response.route_back
        }
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

    agent = PreProcessAgent(model=model, rag=sys_info, db=es_db)

    state = {
        "working_event": e1,
        "files": collector.collected_files,
    }

    builder = StateGraph(PreProcessAgentState)
    builder.add_node("node1", agent.interpre_event)
    builder.add_node("node2", agent.gen_search_query)
    builder.add_node("db_search", agent.search_in_db)
    builder.add_node("node4", agent.search_feedback)

    builder.add_edge(START, "node1")
    builder.add_edge("node1", "node2")
    builder.add_edge("node2", "db_search")
    builder.add_edge("db_search", "node4")
    builder.add_conditional_edges("node4",
        lambda state: "refine_search" if state["route_back"] else "proceed_to_next",
            {
                "refine_search": "node2",
                "proceed_to_next": END
            }
    )

    graph = builder.compile()

    result = graph.invoke(state)

    import pprint
    result["files"] = None
    pprint.pprint(result)
    print(f"len of message: {len(result['message'])}")

if __name__ == "__main__":
    # test()
    main()
