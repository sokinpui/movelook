from langgraph.graph import StateGraph, END, START
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from typing import TypedDict, List, Annotated
import json

from .agent_abc import Agent, add_string_message
from event import Event

class AnalyzeAgentState(TypedDict):
    working_event: Event
    message: Annotated[list[str], add_string_message]

class AnalyzeAgent(Agent):
    def __init__(self, state: AnalyzeAgentState):

