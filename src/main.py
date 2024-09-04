from collector import Collector
from scanner import Scanner
from config import Config
from utils.database import Database
import sys

config = Config(sys.argv[1])

collector_config = config.get_collector_config()
scanner_config = config.get_scanner_config()
db_config = config.get_database_config()

database = Database(db_config)
collector = Collector(collector_config, database)
scanner = Scanner(scanner_config, database)

def main():
  while True:
    try:
      command = input("Please enter a command: ")
      if command == "start collector":
        collector.start()
      elif command == "stop collector":
        collector.stop()
      elif command == "start scanner":
        scanner.start()
      elif command == "stop scanner":
        scanner.stop()
      elif command == "clean":
        database.clear_database()
      elif command == "q":
        scanner.stop()
        collector.stop()
        break
      elif command == "h":
        print("start collector: start the collector module")
        print("stop collector: stop the collector module")
        print("start scanner: start the scanner module")
        print("stop scanner: stop the scanner module")
        print("clean: clean up the database")
        print("q: quit the program")
      else:
        print("Invalid command")
    except KeyboardInterrupt:
      print("keyboard interrupt, stopping all modules")
      scanner.stop()
      collector.stop()

if __name__ == "__main__":
  main()

