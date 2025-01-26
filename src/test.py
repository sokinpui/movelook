from log_collector import Collector
from pattern_extractor import Extractor

import docker
import os
import subprocess
import time


# ensure the network exists
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


home_dir = os.getenv('HOME')
config = f'{home_dir}/work/ml/config.yml'

def test_collector():
    collector = Collector(config)
    collector.process()

def test_extractor():
    extractor = Extractor(config)
    extractor.regex_search()

def test_docker():
    # TODO: successfully create a container, but the code end
    client = docker.DockerClient(base_url='unix:///Users/mac/.colima/default/docker.sock')
    container_name = "es01"
    image = "docker.elastic.co/elasticsearch/elasticsearch:8.17.1"
    network_name = "elastic"
    ports = {'9200/tcp': 9200}
    environment = {
        "discovery.type": "single-node",
        "xpack.security.enabled": "false",
        "xpack.license.self_generated.type": "trial"
    }
    container = client.containers.run(
       image,
       name=container_name,
       network=network_name,
       ports=ports,
       environment=environment,
       detach=True,  # Run in detached mode
       remove=True,  # Automatically remove the container when it exits
    )

while True:
    test_docker()
    time.sleep(10)
