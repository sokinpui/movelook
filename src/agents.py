from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field
from typing import TypedDict, List, Optional, Dict
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

class PreProcessAgentState(TypedDict):
    working_event: Event
    message: str
    files : List[LogFile]
    apps : List[str]

class PreProcessAgent:
    def __init__(self, model: LLMModel, rag: RAGManager, db: ElasticsearchDatabase):
        self.model = model
        self._rag = rag
        self._db = db
        self._logger = Logger()

    def interpre_event(self, state: PreProcessAgentState) -> PreProcessAgentState | dict | None:
        event = state["working_event"]
        files = state["files"]

        self._logger.info(f"agents: {self.__class__.__name__} working on event-id:{event.id}:")

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

        event = state["working_event"]
        message = state["message"]
        apps = state["apps"]

        self._logger.info(f"agents: {self.__class__.__name__} working on event-id: {event.id}:")


        class schema(BaseModel):
            search_queries : str = Field(description=f"""
                                        The json format boolean query to search the database
                                        for log entries related to the provided event.
                                        """)

        sample = []
        for app in apps:

            # get random sample from the database
            random_data = self._db.random_sample(f"log_{app}", cfg.RANDOM_SAMPLE_SIZE)
            for data in random_data:
                sample.append(data["_source"]["content"])

            prompt = pap.filter_logs(event.description, message, apps, sample)
            response = self.model.generate(str(sample) + prompt, schema=schema)

            try:
                queries = json.loads(response.search_queries)
                print(f"search_queries:\n{json.dumps(queries, indent=4)}")
            except Exception as e:
                print(f"search_queries: {response.search_queries}")
                self._logger.error(f"Error parsing search queries to json: {e}")
                exit(1)

            index = f"log_{app}"
            search_result = self._db.scroll_search(queries, index)

            # create alias for collected lines
            resp = self._db.add_alias(index, f"pre_process_{event.id}", filter=queries["query"])

            self._logger.info(f"agents: {self.__class__.__name__} search result for {app}: find {len(search_result)} related lines")


        return



def test():
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

    e1 = Event(description="Is IP address 185.165.29.69 invalid user, I mean in ssh")
    print(f"Event to trace: {e1.description}")

    agent = PreProcessAgent(model=model, rag=sys_info, db=es_db)

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
    # test()
    main()
