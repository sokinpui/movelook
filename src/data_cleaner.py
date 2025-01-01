from elasticsearch import Elasticsearch
from datetime import datetime, timedelta
import yaml
from .es_client import ESClient

with open('config.yml', 'r') as f:
    config = yaml.safe_load(f)
    retention_days = config['cleaner']['interval']
    buffer_index = config['cleaner']['index']
    index_to_cleanup = config['collector']['index']

class BufferManager:
    def __init__(self, config):
        self.es_client = ESClient.get_instance()
        self.retention_period = timedelta(days=retention_days)
        self.buffer_index = buffer_index
        self.get_config(config)

    def get_config(self, config_path):
        with open(config_path, 'r') as file:
            self.config = yaml.safe_load(file)

    def move_data(self, source, dest):
        cutoff_date = datetime.now() - self.retention_period

        reindex_response = self.es_client.reindex({
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

        if reindex_response['total'] > 0:
            print(f"Moved {reindex_response['total']} entries to buffer.")

            # Delete old entries from the source index
            delete_response = self.es_client.delete_by_query(index=source, body={
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

    def move_to_buffer(self):
        self.move_data(index_to_cleanup, buffer_index)

    def cleanup_buffer(self):
        self.move_data(buffer_index, "trash")
        # Cleanup the trash index
        cleanup_response = self.es_client.indices.delete(index="trash")

# Example usage
if __name__ == "__main__":
    pass
