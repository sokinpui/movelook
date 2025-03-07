from abc import ABC, abstractmethod
from langgraph.graph import StateGraph

class Agent(ABC):

    workflow: StateGraph
    graph: StateGraph
    idk: str

    @abstractmethod
    def _build_graph(self):
        pass

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    async def arun(self):
        pass

