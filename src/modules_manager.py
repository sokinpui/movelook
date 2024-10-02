# module manager dynamically loads modules from the modules directory

import importlib.util
import os

# TODO: add load proirity to modules
# TODO: turn on module according to config

class Module_Manager:
    def __init__(self, config):
        self.modules = {}
        self.config = config
        self.modules_dir = config['modules_dir']

    # only load module that are in the config
    def load_modules_from_config(self):
        for module_name in self.config['modules']:
            module_path = os.path.join(self.module_dir, module_name)
            if os.path.isdir(module_path) and os.path.exists(os.path.join(module_path, '__init__.py')):
                spec = importlib.util.spec_from_file_location(module_name, os.path.join(module_path, '__init__.py'))
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                M = getattr(module, 'M')
                self.modules[module_name] = M
            else:
                print(f"Module {module_name} not found in {module_path}")

    def run_modules(self):
        for module_name, M in self.modules.items():
            print(f"Running {module_name}...")
            try:
                M().run()
            except Exception as e:
                print(f"Error in {module_name}: {e}")
                continue

    def sort_modules_by_weight(self):
        w_list = {}
        for module_name in self.config['modules']:
            w_list[module_name] = module_name['weight']
        # sort() function here





