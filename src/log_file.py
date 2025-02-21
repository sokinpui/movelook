
class LogFile:

    file_id = 0

    def __init__(self, filename : str):
        self.filename = filename
        self.summary = None
        LogFile.file_id += 1
        self.id = LogFile.file_id

    def add_file_summary(self, summary: str):
        summary.strip()
        self.summary = summary

class LogFilesList:
    def __init__(self):
        self.log_files = []

    def add_log_file(self, log_file : LogFile):
        self.log_files.append(log_file)


    def get_file(self, file_id : int = -1, file_name: str = "" ) -> LogFile | None:
        for log_file in self.log_files:
            if log_file.id == file_id or log_file.filename == file_name:
                return log_file

        return None

    def get_all_files(self) -> list[LogFile]:
        return self.log_files

