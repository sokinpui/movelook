# plugin_interface.py
from abc import ABC, abstractmethod

class M_API(ABC):

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def stop(self):
        pass


