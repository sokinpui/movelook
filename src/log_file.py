
class LogFile:

    file_id = 0

    def __init__(self, filename : str):
        self.name = filename
        self.summary = None
        LogFile.file_id += 1
        self.id = LogFile.file_id
        self.related_events = []

    def add_file_summary(self, summary: str):
        summary.strip()
        self.summary = summary

    def to_dict(self) -> dict:
        return self.__dict__
