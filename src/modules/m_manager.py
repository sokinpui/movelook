import importlib
import os
from m_api import M_API
import sys

# Load the module dynamically, where each module is a subdir with __init__.py

class M_Manager:
    def __init__(self, module_path):
        self.modules = {}
        self.path = module_path

    def load_modules(self):
        for module in os.listdir(self.path):
            if module == '__pycache__' or module == '__init__.py':
                continue
            module_name = module[:-3]
            try:
                module = importlib.import_module(f'{self.path}.{module_name}')
                for attr in dir(module):
                    plugin_class = getattr(module, attr)
                    if isinstance(plugin_class, type) and issubclass(plugin_class, M_API):
                        self.modules[module_name] = plugin_class()
            except Exception as e:
                print(f'Error loading module: {module} - {e}')

    def run_modules(self):
        for module in self.modules.values():
            data = "Hello World"
            print(module)
            module.run(data)





