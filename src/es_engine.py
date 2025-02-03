# start docker or singularity container

import os
import docker
from elasticsearch import Elasticsearch
import subprocess
import yaml
import time
import requests

# if on mac, then use docker, if on linux cluster, if singularity is installed, use singularity, otherwise use docker


dir_path = os.path.dirname(os.path.realpath(__file__))
config_path = os.path.join(dir_path, 'devconfig.yml')
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

# Run the container
home_dir = os.getenv('HOME')

mac_es_docker_setup = config['docker']['es']
kibana_docker_setup = config['docker']['kibana']

def _start_docker_on_mac(container_setup):
    try:
        # convert to string
        colima_memory = str(config["colima"]["memory"])
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
    volume_name = list(config['docker']['es']['volumes'].keys())[0]
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

# start the container only
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
        self.instance = Elasticsearch('http://localhost:9200')
        print('Connected to Elasticsearch')
        print('Elasticsearch version, is running via Container')
        return self.instance
