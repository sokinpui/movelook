from abc import ABC, abstractmethod

from database import Database, ElasticsearchDatabase
from logger import Logger
import config as cfg
from log_file import LogFile
from event import Event
import data_struct

import os
from elasticsearch.exceptions import NotFoundError
from datetime import datetime

## data structure used in database


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

        return log_files

    def collect_events(self, file: str) -> list[Event]:
        events = []

        with open(file, 'r') as f:
            lines = f.readlines()

        # grouping lines into events, split by empty line
        event_description = ""

        for line in lines:
            if line.strip():
                event_description += line.strip()
            else:
                if event_description:
                    event = Event(description=event_description)
                    events.append(event)
                    event_description = ""

        return events

    def insert_events_to_db(self, db: Database, events: list[Event]):
        for event in events:
            db.insert(event.to_dict(), cfg.INDEX_EVENTS_STORAGE)
            self._logger.info(f"collector: Inserted event {event.to_dict()}")

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
                line_of_log = data_struct.LineOfLogFile(
                        content=line,
                        line_number=i,
                        name=log.name,
                        id=log.id,
                        timestamp=datetime.now()
                )
                db.insert(line_of_log.to_dict(), cfg.INDEX_LOG_FILES_STORAGE)
            self._save_last_line_read(log, db, len(file_lines))

            self._logger.info(f"collector: Inserted {len(file_lines) - last_line_read} lines of {log.name}, range: {last_line_read} - {len(file_lines)}")


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
            return last_line_status[0]['_source']['last_line_read']
        else:
            return 0

    def _save_last_line_read(self, log_file: LogFile, db: Database, line_number: int):
        last_line_status = data_struct.LastLineRead(
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
        except NotFoundError:
            db.insert(data=last_line_status.to_dict(), index=cfg.INDEX_LAST_LINE_STATUS)
        except Exception as e:
            self._logger.error(f"Error updating last line read for log file {log_file.name}: {e}")
            exit(1)

def main():

    import random

    es_db = ElasticsearchDatabase()

    dir = "../log/"
    collector = NewCollector(dir)
    collector.insert_logs_to_db(db=es_db, files=collector.log_files)

    events_file = "./prompt/events.txt"
    events = collector.collect_events(file=events_file)

    collector.insert_events_to_db(db=es_db, events=events)


    # random_snapshot_size = 2
    #
    # # random snapshot
    # for file in collector.log_files:
    #     start = random.randint(0, file.get_total_lines(db=es_db)-random_snapshot_size)
    #     size = random_snapshot_size
    #
    #     snapshot = file.get_snapshot(
    #             id=file.id,
    #             earliest_timestamp=datetime(2021, 1, 1),
    #             start=start,
    #             size=size,
    #             db=es_db
    #     )
    #
    #     print(f"Snapshot of {file.name} from line {start} to {size}, total lines: {file.get_total_lines(db=es_db)}")
    #     print(snapshot)

if __name__ == "__main__":
    main()
