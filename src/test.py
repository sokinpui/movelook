from log_collector import Collector
from pattern_extractor import Extractor

import os
import subprocess
import time


# ensure the network exists
network_command = [
    "docker", "network", "create", "es-net"
]

# check if the network exists
network_command = [
    "docker", "network", "ls", "--filter", "name=es-net"
]

# check if the container exists
container_command = [
    "docker", "ps", "-a", "--filter", "name=elasticsearch_container"
]

# Define the Docker command
docker_command = [
    "docker", "run",
    "--name", "elasticsearch_container",
    "--network", "es-net",
    "-p", "9200:9200",
    "-e", "xpack.security.enabled=false",
    "-e", "discovery.type=single-node",
    "docker.elastic.co/elasticsearch/elasticsearch:8.7.0"
]

# Execute the command
# try:
#     if subprocess.run(network_command).returncode == 0:
#         print("Elasticsearch network already exists.")
#     else:
#         subprocess.Popen(network_command)
#         print("Elasticsearch network created successfully.")
#
#     # Check if the container exists
#     if subprocess.run(container_command).returncode == 0:
#         print("Elasticsearch container already exists.")
#     else:
#         subprocess.Popen(docker_command)
#         print("Elasticsearch container started successfully.")
# except subprocess.CalledProcessError as e:
#     print(f"Error occurred: {e}")


from es_client import ESClient

# es_client = ESClient.get_instance()


home_dir = os.getenv('HOME')
config = f'{home_dir}/work/ml/config.yml'
#
# collector = Collector(config)
#
# # logging with timestamp
# collector.process()

extractor = Extractor(config)
extractor.regex_search()





