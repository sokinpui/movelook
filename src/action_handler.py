import logging
from es_client import ESClient
import yaml

# Load configuration from a file
def load_config(config_path):
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

class ActionHandler:
    def __init__(self, config):
        self.config = config
        self.es_client = ESClient.get_instance()
        self.get_config(config)

    def get_config(self, config_path):
        with open(config_path, 'r') as file:
            self.config = yaml.safe_load(file)

    def check_messages(self):
        # Query Elasticsearch index for messages
        index = 'logs'  # Replace with your log index name
        query = {
            "query": {
                "match_all": {}
            }
        }

        response = self.es_client.search(index=index, body=query)
        # get the field "messages" from the response
        messages = [hit['_source']['message'] for hit in response['hits']['hits']]

        # Check messages against defined patterns
        for message in messages:
            self.handle_action(message)

    def handle_action(self, message):
        if message == "log_warning":
            self.log_warning(message)
        elif message == "send_alert":
            self.send_alert(message)

    def log_warning(self, message):
        logging.warning(f"Warning logged: {message}")
        self.es_client.index(index='warnings', body={"message": message})

    def send_alert(self, message):
        logging.info(f"Alert sent: {message}")
        # Implement actual alert sending logic here

# Usage example
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)  # Configure logging
    config_path = 'config.yml'  # Path to your config file
    config = load_config(config_path)

    action_handler = ActionHandler(config)

    # Check messages in Elasticsearch and handle actions
    action_handler.check_messages()
