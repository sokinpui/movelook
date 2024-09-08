# module manager dynamically loads modules from the modules directory

import importlib.util
import os

class Module_Manager:
    def __init__(self, module_dir):
        self.module_dir = module_dir
        self.modules = {}

    def load_modules(self):
        for module_name in os.listdir(self.module_dir):
            module_path = os.path.join(self.module_dir, module_name)
            if os.path.isdir(module_path) and os.path.exists(os.path.join(module_path, '__init__.py')):
                spec = importlib.util.spec_from_file_location(module_name, os.path.join(module_path, '__init__.py'))
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                M = getattr(module, 'M')
                self.modules[module_name] = M

    def run_modules(self):
        for module_name, M in self.modules.items():
            print(f"Running {module_name}...")
            M().run()
