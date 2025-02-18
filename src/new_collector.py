from abc import ABC, abstractmethod
from database import Database


class LogSource(ABC):
    @abstractmethod
    def collect_logs(self):
        pass

class FileLogSource(LogSource):
    def __init__(self, file_path: str):
        self.file_path = file_path

    def collect_logs(self):
        # Read logs from a file

        # Insert logs into database
        pass

    def _insert_data(self,
                    data : dict,
                    database : Database,
                    field : str
                    ):
        pass

class NewCollector:
    def __init__(self, log_source: LogSource):
        self.log_source = log_source

    def collect(self):
        self.log_source.collect_logs()
        pass
