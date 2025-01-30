# start docker or singularity container

import os
import docker
from elasticsearch import Elasticsearch
import subprocess
import yaml

# if on mac, then use docker, if on linux cluster, if singularity is installed, use singularity, otherwise use docker


dir_path = os.path.dirname(os.path.realpath(__file__))
config_path = os.path.join(dir_path, 'config.yml')
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

# Run the container
home_dir = os.getenv('HOME')

class ESEngine():
    def __init__(self):
        self.container = None
        return_code = self.__start_container()
        if return_code == 0:
            self.instance = self.get_instance()
        elif return_code == 1:
            print('Failed to start container')


    def __start_container(self):
        if os.uname().sysname == 'Darwin':
            print('Starting Docker on Mac')
            return_code = self.__start_docker_on_mac()
            if return_code == 1:
                print('Failed to start docker on Mac')
                return 1
        elif os.uname().sysname == 'Linux':
            if os.system('which singularity') == 0:
                pass
            else:
                pass
        elif os.uname().sysname == 'Windows':
            # not supported
            print('Windows is not supported')

    def __start_docker_on_mac(self):
        try:
            res = subprocess.run(['colima', 'status'], capture_output=True, text=True)
            if 'level=fatal' in res.stderr:
                print('Starting colima...')
                # config make the memory configurable
                subprocess.run(['colima', 'start', '--memory', '4'])
            else:
                print('Colima is already running.')
        except Exception as e:
            print(e)
            return 1

        os.environ['DOCKER_HOST'] = f'unix://{home_dir}/.colima/default/docker.sock'
        client = docker.from_env()

        container_name   = config["docker"]["container_name"]
        image   = config["docker"]["image"]
        network_name   = config["docker"]["network_name"]
        ports   = config["docker"]["ports"]
        environment   = config["docker"]["environment"]

        # check if the network exists
        try:
            network = client.networks.get(network_name)
            print('Network exists')
        except Exception as e:
            print('Network does not exist')
            network = client.networks.create(network_name)
            print('Network created')

        # remove the old container
        try:
            old_containers = client.containers.get("es01")
            if old_containers.name == 'es01':
                old_containers.remove(force=True)
                print('Removed old container')
        except Exception as e:
            pass

        # Run the container
        try:
            container = client.containers.run(
               image,
               name=container_name,
               network=network_name,
               ports=ports,
               environment=environment,
               detach=True,  # Run in detached mode
               # remove=True  # Automatically remove the container when it exits
               remove=False
            )
            print('Started container')
        except Exception as e:
            return 1
            print(e)

        return 0


    def __start_singularity(self):
        pass

    # data store outside of container

# TODO: work with ES security and authentication, cert and key files
class ESClient:

    def __init__(self):
        # self.es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
        self.instance = None

    def get_instance(self):
        self.instance = Elasticsearch('http://localhost:9200')

        return self.instance
