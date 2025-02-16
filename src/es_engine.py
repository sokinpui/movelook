# start docker or singularity container

import os
import docker
from elasticsearch import Elasticsearch
import subprocess
import yaml
import time
import requests
from datetime import datetime
import random

# if on mac, then use docker, if on linux cluster, if singularity is installed, use singularity, otherwise use docker


dir_path = os.path.dirname(os.path.realpath(__file__))
config_path = os.path.join(dir_path, 'devconfig.yml')
with open(config_path, 'r') as f:
    dev_config = yaml.safe_load(f)

# Run the container
home_dir = os.getenv('HOME')

mac_es_docker_setup = dev_config['docker']['es']
kibana_docker_setup = dev_config['docker']['kibana']

def _start_docker_on_mac(container_setup):
    """
    start docker and run Elasticsearch container
    """
    try:
        # convert to string
        colima_memory = str(dev_config["colima"]["memory"])
        res = subprocess.run(['colima', 'status'], capture_output=True, text=True)
        if 'level=fatal' in res.stderr:
            print('Starting colima...')
            # config make the memory configurable
            subprocess.run(['colima', 'start', '--memory', colima_memory])
        else:
            print('Colima is already running.')
    except Exception as e:
        print(e)
        return 1

    os.environ['DOCKER_HOST'] = f'unix://{home_dir}/.colima/default/docker.sock'
    client = docker.from_env()

    # volume is the key name in the config files, how to get the value?
    volume_name = list(dev_config['docker']['es']['volumes'].keys())[0]
    print(f'Volume name: {volume_name}')
    try:
        # Check if the volume already exists
        volume = client.volumes.get(volume_name)
        print(f"Volume '{volume_name}' already exists. Using it.")
    except docker.errors.NotFound:
        # If the volume does not exist, create it
        volume = client.volumes.create(name=volume_name)
        print(f"Volume '{volume_name}' created.")
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

    # check if the network exists
    try:
        network = client.networks.get(container_setup['network'])
        print('Network exists')
    except Exception as e:
        print('Network does not exist')
        network = client.networks.create(container_setup['network'])
        print('Network created')

    # remove the old container
    try:
        old_containers = client.containers.get(container_setup['name'])
        if old_containers.name == container_setup['name']:
            old_containers.remove(force=True)
            print('Removed old container')
    except Exception as e:
        pass

    # Run the container
    try:
        container = client.containers.run(**container_setup)
        print(f'Started container for {container_setup["name"]}')
        print(f'Container ID: {container.id}')
    except Exception as e:
        print(e)
        return 1

    return 0

# simple wait logic to check if ES is ready to use
def _is_es_ready():
    try:
        requests.get('http://localhost:9200')
        print('ES is up!')
        return True
    except requests.exceptions.ConnectionError:
        print('Waiting for ES to start...')
        time.sleep(1)
        return False
    except Exception as e:
        print(f'An error occurred: {e}')
        return False

def start_container():
    if os.uname().sysname == 'Darwin':
        print('Starting Docker on Mac')
        return_code = _start_docker_on_mac(mac_es_docker_setup)
        if return_code == 1:
            print('Failed to start docker on Mac')
            return return_code
        while not _is_es_ready():
            pass
        return return_code
    elif os.uname().sysname == 'Linux':
        if os.system('which singularity') == 0:
            pass
        else:
            pass
    elif os.uname().sysname == 'Windows':
        print('Windows is not supported')

def start_kibana_gui():
    """
    start kibana gui for Elasticsearch
    """
    while not _is_es_ready():
        pass
    return_code = _start_docker_on_mac(kibana_docker_setup)
    print('kibana is now running')
    print('aceess kibana at http://localhost:5601')
    if return_code == 1:
        print('Failed to start docker on Mac')
        return 1
    print('kibana is now running')
    return return_code

def remove_container(name):
    try:
        client = docker.from_env()
        container = client.containers.get(name)
        container.remove(force=True)
    except Exception as e:
        print(f'An error occurred: {e}')
        pass



# TODO: work with ES security and authentication, cert and key files
class ESClient:

    def __init__(self):
        # self.es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
        self.instance = None

    def get_instance(self):
        try:
            requests.get('http://localhost:9200')
        except requests.exceptions.ConnectionError as e:
            print('Elasticsearch is not running')
            print(e)
        self.instance = Elasticsearch([ 'http://localhost:9200' ])
        return self.instance

    def get_files_size(self, file_name):
        # TODO: will count duplicate lines, need to fix, should be error or calling `collector.py` too many times
        """
        Get the size of the file in the Elasticsearch
        file_name in query is the path of the file
        """
        es = self.get_instance()
        # count the unique line of the file
        query = {
            "size": 0,
            "query": {
                "match": {
                    "path": file_name
                }
            },
            "aggs": {
                "lines": {
                    "cardinality": {
                        "field": "line_number"
                    }
                }
            }
        }
        response = es.search(index=dev_config['collector']['index'], body=query)
        return response['hits']['total']['value']


    def get_files(self) -> list:
        """
        Get a list of files name store in the Elasticsearch, assume number of files is less than 1000
        """
        es = self.get_instance()
        query = {
            "size": 0,
            "aggs": {
                "files": {
                    "terms": {
                        "field": "path.keyword",
                        "size": 1000
                    }
                }
            }
        }

        response = es.search(index=dev_config['collector']['index'], body=query)
        files = [bucket['key'] for bucket in response['aggregations']['files']['buckets']]
        return files

    def get_file_snapshot(self, snapshot_size: int, earliest_timestamp: datetime, file_name : str,  index_name: str) -> dict:
        """
        Fetch a snapshot of log lines from Elasticsearch for a given file name.
        the snapshot size is configurable by devconfig['llm']['snapshot_size']
        Too large snapshot size may cause exceeding the output limit of the LLM model.
        default snapshot size is 1000
        """
        es = self.get_instance()

        # Initial query with scroll enabled to fetch all logs after earliest_timestamp
        # make es field configurable
        query = {
            "size": 1000,  # Fetch in chunks
            "query": {
                "bool": {
                    "must": [
                        {"range": {"timestamp": {"gt": earliest_timestamp.strftime("%Y-%m-%dT%H:%M:%S")}}},
                        {"match": {"path": file_name}}  # Filter by file name (assuming 'path' stores file name)
                    ]
                }
            },
            "sort": [{"lineNumber": "asc"}]  # Sort by line number instead of timestamp
        }

        # count the lines return in the search



# Start scrolling
        response = es.search(
                index=index_name,
                body=query,
                scroll="2m"
                )
        scroll_id = response["_scroll_id"]
        scroll_size = len(response["hits"]["hits"])

        log_data = {}

        while scroll_size > 0:
            for hit in response["hits"]["hits"]:
                log_data[hit["_source"]["lineNumber"]] = hit["_source"]["line"]
            response = es.scroll(scroll_id=scroll_id, scroll="2m")
            scroll_id = response["_scroll_id"]
            scroll_size = len(response["hits"]["hits"])

        # Clear the scroll context in Elasticsearch
        es.clear_scroll(scroll_id=scroll_id)

        # If there's not enough data, return all available logs
        if len(log_data) <= snapshot_size:
            return log_data

        # Randomly select continue 'snapshot_size' lines from the fetched logs
        line_numbers = list(log_data.keys())
        start_index = random.randint(0, len(line_numbers) - snapshot_size)
        snapshot = {}
        for i in range(start_index, start_index + snapshot_size):
            snapshot[line_numbers[i]] = log_data[line_numbers[i]]

        return snapshot

def main():
    start_container()
    start_kibana_gui()
    pass

if __name__ == '__main__':
    main()
