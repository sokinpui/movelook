from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Optional, Dict
from llm_model import LLMModel, GeminiModel
from llm_agents import LogAnalyzeAgent, AgentState

STOP = "stop"
CONTINUE = "continue"

def define_graph():
    """
    draw the graph here
    """
    model = GeminiModel()
    agent = LogAnalyzeAgent(model=model)

    graph = StateGraph(AgentState)

    graph.add_node(agent.pop_next_event.__name__, agent.pop_next_event)

    graph.add_conditional_edges(
            agent.pop_next_event.__name__,
            agent.check_stop,
            {
                STOP: END,
                CONTINUE: agent.pop_next_event.__name__
            }
    )

    graph.set_entry_point(agent.pop_next_event.__name__)

    compiled_graph = graph.compile()
    return compiled_graph
