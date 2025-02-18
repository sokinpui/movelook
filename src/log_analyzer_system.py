from container_manger import ContainerManager
from collector import Collector
from database import Database
from llm_bot import LLMBot

class LogAnalyzerSystem:
    def __init__(self,
                 container_manager : ContainerManager,
                 collector : Collector,
                 database : Database,
                 llm_bot : LLMBot,
                 ):
        self.container_manager = container_manager
        self.collector = collector
        self.database = database
        self.llm_bot = llm_bot

    def run(self):
        pass
