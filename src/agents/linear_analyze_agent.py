from langgraph.graph import StateGraph, END, START
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from typing import TypedDict, List, Annotated, Any, Callable
import json

from .agent_abc import Agent, add_string_message
from event import Event
from database import ElasticsearchDatabase
from llm_model import LLMModel
from logger import Logger
import config as cfg

class LinearAnalyzeAgentState(TypedDict):
    working_event: Event
    message: Annotated[list[str], add_string_message]
    start: int # start index of the chunk
    working_file_ids: list[str] # list of file ids

class ESTextChunkManager:
    """
    Manage the chunk of text to analyze.
    Retrieve the chunk from Elasticsearch

    Args:
        id: The id that is used to retrieve the text
        field: field to retrieve the text
        index: index of the document
        db: ElasticsearchDatabase instance
    """
    def __init__(self, id: Any, field : str, index: str, db: ElasticsearchDatabase):
        self.id = id
        self.field = field
        self._db = db
        self._index = index

        self.hits = self._get_all_hits()
        self.total_hits = len(self.hits)

        self.start = 0
        self._start_shift = 0

        self.hits_in_current_chunk = 0
        self.current_chunk = None

    def _build_chunk(self, initial_size: int, start: int, hits: list, max_len: int, len_fn: Callable[[str], int]) -> str:
        """
        Build the chunk of text from the hits

        Args:
            initial_size: initial size of the chunk
            start: start index of the hits
            hits: list of hits return from the Elasticsearch `response["hits"]["hits"]`
            max_len: maximum length of the chunk
            len_fn: function to calculate the length of the text
        """
        chunk = ""
        total_tokens = 0
        start = start
        hits_length = len(hits)
        current_size = initial_size  # Start with the initial size (e.g., 512)
        count = 0

        while total_tokens < max_len and start < hits_length:
            end = start + current_size

            current_hits = hits[start:end]
            if not current_hits:
                break  # No more hits to process

            tmp = "".join(hit["_source"]["content"] for hit in current_hits)
            tmp_tokens = len_fn(tmp)

            if total_tokens + tmp_tokens > max_len:
                if current_size == 1:
                    break  # Smallest size still exceeds; skip remaining
                current_size = max(1, current_size // 2)  # Halve the size
                continue  # Retry with smaller size at the same start position

            # Add the chunk and advance
            count += current_size
            chunk += tmp
            total_tokens += tmp_tokens
            start += current_size

        self._start_shift = start
        self.hits_in_current_chunk = count

        return chunk

    def _get_all_hits(self):
        """
        Get all the hits from the Elasticsearch
        """
        query = {
            "query": {
                "match": {
                    "id": self.id
                }
            },
            "_source": [self.field]
        }

        return self._db.scroll_search(index=self._index, query=query)

    def get_next_chunk(self, max_tokens: int, token_count: Callable[[str], int]) -> str | None:
        """
        Get the next chunk of text to analyze,
        the status of the chunk is stored in the class
        Start index is updated after each call

        Args:
            max_tokens: maximum tokens to analyze
            token_count: function to count the tokens in the text

        Returns:
            str: chunk of text
            None: if no more hits to process

        """
        if self.start >= len(self.hits):
            print("No more hits to process")
            return None

        chunk = self._build_chunk(2**10, self.start, self.hits, max_tokens, token_count)

        self.current_chunk = chunk
        self.start = self._start_shift

        return chunk

    def get_current_chunk(self):
        return self.current_chunk

class LinearAnalyzeAgent(Agent):
    def __init__(self, model : LLMModel, db : ElasticsearchDatabase,
                 state_dict=LinearAnalyzeAgentState):

        self._model = model

        self.workflow = StateGraph(state_dict)
        self._build_graph()
        # self.graph = self.workflow.compile()

        self._db = db
        self._logger = Logger()

        self._memory_size = cfg.MEMRORY_TOKENS_LIMIT

    def run(self, state: LinearAnalyzeAgentState) -> LinearAnalyzeAgentState:
        """
        run the agent synchronously with `invoke` method
        """
        state = self.graph.invoke(state)
        return state

    async def arun(self, state: LinearAnalyzeAgentState) -> LinearAnalyzeAgentState:
        """
        run the agent asynchronously with `invoke` method
        """
        state = await self.graph.ainvoke(state)
        return state

    def _build_graph(self):
        pass

    def next_chunk(self, state: LinearAnalyzeAgentState):
        """
        Get the next chunk of text to analyze
        """
        pass

    def chunk_analysis(self, state: LinearAnalyzeAgentState):
        """
        Analyze the chunk of text
        """
        pass

    def memorize(self, state: LinearAnalyzeAgentState):
        """
        Memorize the result
        """
        pass

    def _recall_memory(self, state: LinearAnalyzeAgentState):
        """
        Recall the memory
        """
        pass

    def _pop_file_id(self, state: LinearAnalyzeAgentState):
        """
        Pop the finished file id from the list
        """
        pass

    def _get_working_files(self, state: LinearAnalyzeAgentState):
        """
        _get_working_file:
            get all the files ids from the database
            the index is pre-defined in the config file in the format of "pre_process_{event_id}"
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
    agent = LinearAnalyzeAgent(model, db)

    state = {
        "working_event": Event("asdfasdfsd"),
    }

    chunk_manager = ESTextChunkManager(6, "content", cfg.get_pre_process_index(1), db)

    max_tokens = model.context_size - cfg.MEMRORY_TOKENS_LIMIT

    print(f"total hits: {len(chunk_manager.hits)}")

    while True:
        # Get the next chunk
        chunk = chunk_manager.get_next_chunk(max_tokens, model.token_count)

        # If no more chunks, break the loop
        if chunk is None:
            print("No more chunks to process. Test complete.")
            break

        # Print the state of the loop
        print(f"Start index: {chunk_manager.start}, Total tokens: {model.token_count(chunk)}, hits in this round: {chunk_manager.hits_in_current_chunk}")

if __name__ == "__main__":
    main()
