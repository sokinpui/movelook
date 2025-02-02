from elasticsearch import Elasticsearch
from datetime import datetime, timedelta
import yaml
from es_engine import ESClient
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
config_path = os.path.join(dir_path, 'devconfig.yml')
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)
    retention_days = config['cleaner']['interval']
    buffer_index = config['cleaner']['index']
    index_to_cleanup = config['collector']['index']

class BufferManager:
    def __init__(self, config):
        self.es = ESClient().get_instance()
        self.retention_period = timedelta(days=retention_days)
        self.buffer_index = buffer_index
        self.get_config(config)

    def get_config(self, config_path):
        with open(config_path, 'r') as file:
            self.config = yaml.safe_load(file)

    # move data from source index to destination index
    def move_data(self, source, dest):
        cutoff_date = datetime.now() - self.retention_period

        reindex_response = self.es.reindex({
            "source": {
                "index": source,
                "query": {
                    "range": {
                        "timestamp": {  # Change 'timestamp' to your date field
                              "lt": cutoff_date
                          }
                    }
                }
            },
            "dest": {
                "index": dest
            }
        })

        # Check if any documents were moved
        if reindex_response['total'] > 0:
            print(f"Moved {reindex_response['total']} entries to buffer.")

            # Delete old entries from the source index
            delete_response = self.es.delete_by_query(index=source, body={
                "query": {
                    "range": {
                        "timestamp": {
                            "lt": cutoff_date
                        }
                    }
                }
            })

            print(f"Deleted {delete_response['deleted']} old documents from {source}")
        else:
            print("No documents to move.")

    # move data from the index to the buffer
    def move_to_buffer(self):
        self.move_data(index_to_cleanup, buffer_index)

    # cleanup the buffer after the retention period
    def cleanup_buffer(self):
        self.move_data(buffer_index, "trash")
        # Cleanup the trash index
        cleanup_response = self.es.indices.delete(index="trash")

# Example usage
if __name__ == "__main__":
    pass
