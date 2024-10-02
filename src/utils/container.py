# create container for elasticsearch database
from .database import Database

# state in config['container']
# port number
# name of the container
# singularity or docker
# localhots
# forward port

class Container():
    def __init__(self, config):
        self.config = config

    def create_container(self):
        pass

    def start_coinatiner(self):
        pass

    def stop_container(self):
        pass

    def remove_container(self):
        pass
