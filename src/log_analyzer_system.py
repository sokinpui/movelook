from container_manger import ContainerManager, DockerManager
from new_collector import NewCollector
from database import Database, ElasticsearchDatabase
from llm_bot import LLMBot

class LogAnalyzerSystem:
    def __init__(self,
                 container_manager : ContainerManager,
                 collector : NewCollector,
                 database : Database,
                 llm_bot : LLMBot,
                 ):
        self.container_manager = container_manager
        self.collector = collector
        self.database = database
        self.llm_bot = llm_bot

    def run(self):
        pass

def main():
    pass

if __name__ == '__main__':
    main()
