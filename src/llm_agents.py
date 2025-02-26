from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field
from typing import TypedDict, List, Optional, Dict

from llm_model import LLMModel, GeminiModel
from event import Event
from log_file import LogFile
import prompt.agent as pa

STOP = "stop"
CONTINUE = "continue"

class AgentState(TypedDict):
    events: List[Event]
    working_event: Event
    explanation_of_working_event: str
    stop: bool

class LogAnalyzeAgent:
    def __init__(self, model: LLMModel):
        self.model = model

    def pop_next_event(self, state: AgentState) -> AgentState:
        """
        Pop the next event from the list of events and set it as the working event
        explain what information and application are involved in the event
        """

        if not state['events']:
            state['stop'] = True
            return state

        event = state['events'].pop()

        task = f"""
        you are ask to analyze a event:
        - what information are tracing in this event?
        - what application is involved?
        - no explanation needed
        - answer in short
        {event.name}, {event.description}
        """

        state['explanation_of_working_event'] = self.model.generate(pa.SYSTEM_PROMPT + task, None)
        state['working_event'] = event

        print(f"working event: {event.name}")
        print(f"explanation: {state['explanation_of_working_event']}")

        print(f"events left: {len(state['events'])}")

        return state

    def select_files(self, state: AgentState) -> AgentState:
        """
        Select the files that are related to the working event
        """

        event = state['working_event']
        files = event.related_files

        task = f"""
        you are ask to select the files that are related to the event:
        """

        return state

    def check_stop(self, state: AgentState) -> str:
        return STOP if state['stop'] else CONTINUE

def main():

    from database import ElasticsearchDatabase
    from new_collector import NewCollector
    from graph import define_graph

    events_files = "./prompt/events.txt"
    log_dir = "../log"

    db = ElasticsearchDatabase()
    collector = NewCollector(dir=log_dir)

    events = collector.collect_events(events_files)

    initial_state = {
        'events': events,
        'working_event': None,
        'stop': False
    }

    graph = define_graph()
    graph.invoke(initial_state)

if __name__ == "__main__":
    main()






