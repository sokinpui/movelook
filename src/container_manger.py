from abc import ABC, abstractmethod

class ContainerManager(ABC):
    @abstractmethod
    def start_container(self, container_id : str):
        pass

    @abstractmethod
    def stop_container(self, container_id : str):
        pass

    @abstractmethod
    def get_container_status(self, container_id : str):
        pass

class DockerManager(ContainerManager):
    def start_container(self, container_id : str):
        print(f"Starting container {container_id} using Docker")

    def stop_container(self, container_id : str):
        print(f"Stopping container {container_id} using Docker")

    def get_container_status(self, container_id : str):
        print(f"Getting status of container {container_id} using Docker")
