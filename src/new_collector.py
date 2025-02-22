from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from typing import Optional

from database import Database, ElasticsearchDatabase
from logger import Logger
import config as cfg
from log_file import LogFile

import os
from datetime import datetime
from elasticsearch.exceptions import NotFoundError

## data structure used in database

@dataclass
class BaseData:
    def to_dict(self):
        return asdict(self)

@dataclass
class LineOfLogFile(BaseData):
    content: str
    line_number: int
    name: str
    timestamp: datetime

    def to_dict(self):
        data = asdict(self)
        # Convert datetime objects to strings
        if isinstance(data['timestamp'], datetime):
            data['timestamp'] = data['timestamp'].isoformat()  # Convert to ISO 8601 format
        return data

@dataclass
class LastLineRead(BaseData):
    last_line_read: int
    id: int
    name: str

class NewCollector:

    def __init__(self, dir: str):
        self._logger = Logger()
        self._dir = dir
        self.log_files = self.collect_logs(dir)

    def collect_logs(self, dir: str) -> list[LogFile]:

        log_files = []

        # collect logs recursively from the directory
        for root, dirs, files in os.walk(dir):
            for log in files:

                try:
                    log_path = os.path.join(root, log)

                    log_file = LogFile(log_path)
                    log_files.append(log_file)
                    self._logger.info(f"Collected log file {log_file.to_dict()}")
                except Exception as e:
                    self._logger.error(f"Error collecting log file {log}: {e}")

        self._logger.info(f"Collected {len(log_files)} log files")

        return log_files

    def insert_logs_to_db(self, db: Database, files: list):
        for log in files:
            try:
                last_line_read = self._get_last_line_read(log, db)
            except Exception as e:
                self._logger.error(f"Error getting last line read for log file {log.name}: {e}")
                last_line_read = 0

            with open(log.name, 'r') as f:
                file_lines = f.readlines()

            if last_line_read > len(file_lines):
                last_line_read = 0
                self._save_last_line_read(log, db, last_line_read)

            for i in range(last_line_read, len(file_lines)):
                line = file_lines[i]
                line_of_log = LineOfLogFile(
                        content=line,
                        line_number=i,
                        name=log.name,
                        timestamp=datetime.now()
                )
                db.insert(line_of_log.to_dict(), cfg.INDEX_LOG_FILES_STORAGE)
            self._save_last_line_read(log, db, len(file_lines))

            self._logger.info(f"Inserted {len(file_lines) - last_line_read} lines of {log.name}")


    def _get_last_line_read(self, log_file: LogFile, db: Database) -> int:
        query = {
            "query": {
                "match": {
                    "id": log_file.id
                }
            },
            "_source": ["last_line_read"]
        }
        last_line_status = db.search(query=query, index=cfg.INDEX_LAST_LINE_STATUS)
        if last_line_status:
            self._logger.info(f"Last line read found for log file {log_file.name}")
            return last_line_status[0]['_source']['last_line_read']
        else:
            self._logger.info(f"No last line read found for log file {log_file.name}")
            return 0

    def _save_last_line_read(self, log_file: LogFile, db: Database, line_number: int):
        last_line_status = LastLineRead(
                last_line_read=line_number,
                id=log_file.id,
                name=log_file.name
        )
        update_data = {
            "doc": last_line_status.to_dict(),
            "doc_as_upsert": True
        }

        try:
            db.update(
                    index=cfg.INDEX_LAST_LINE_STATUS,
                    id=log_file.id,
                    data=update_data
                    )
            self._logger.info(f"Updated last line read for log file {log_file.name}")
        except NotFoundError:
            self._logger.info(f"index {cfg.INDEX_LAST_LINE_STATUS} not found")
            db.insert(data=last_line_status.to_dict(), index=cfg.INDEX_LAST_LINE_STATUS)
        except Exception as e:
            self._logger.error(f"Error updating last line read for log file {log_file.filepath}: {e}")
            exit(1)

def main():
    es_db = ElasticsearchDatabase()

    dir = "../log/"
    collector = NewCollector(dir)
    collector.insert_logs_to_db(db=es_db, files=collector.log_files)

if __name__ == "__main__":
    main()
