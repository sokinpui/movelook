#tmake a manager instance and load and run the modules
from modules_manager import Module_Manager

manager = Module_Manager('modules')
manager.load_modules()
manager.run_modules()

