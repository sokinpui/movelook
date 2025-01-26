# start docker or singularity container

import os
import docker

# if on mac, then use docker, if on linux cluster, if singularity is installed, use singularity, otherwise use docker


# if on mac, use colima to start docker daemon
# Define the container parameters
# TODO: make these parameters configurable
container_name = "es01"
image = "docker.elastic.co/elasticsearch/elasticsearch:8.17.1"
network_name = "elastic"
ports = {'9200/tcp': 9200}
environment = {
    "discovery.type": "single-node",
    "xpack.security.enabled": "false",
    "xpack.license.self_generated.type": "trial"
}

# Run the container

class ESEngine():
    def __init__(self):
        self.container = None
        if os.uname().sysname == 'Darwin':
            print('Starting Docker on Mac')
            self.__start_docker()
            pass
        elif os.uname().sysname == 'Linux':
            if os.system('which singularity') == 0:
                pass
            else:
                pass
        elif os.uname().sysname == 'Windows':
            # not supported
            print('Windows is not supported')

    def __start_docker(self):
        # start docker daemon
        if os.uname().sysname == 'Darwin':
            os.system('colima start --memory 4')
        elif os.uname().sysname == 'Linux':
            os.system('systemctl start docker')
        client = docker.from_env()
        try:
            self.container = client.containers.run(
                image,
                name=container_name,
                network=network_name,
                ports=ports,
                environment=environment,
                detach=True,  # Run in detached mode
                remove=True,  # Automatically remove the container when it exits
            )
            print(f"Container {container_name} is running.")
        except Exception as e:
            print(f"Error: {e}")

    def __start_singularity(self):
        pass

    # data store outside of container

ese = ESEngine()
