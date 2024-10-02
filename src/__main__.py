# from file in the same directory import class
from collector import Collector
from scanner import Scanner
from config import Config
from utils.database import Database
import sys
import argparse
import os


def main():
    config = Config(sys.argv[1])

    collector_config = config.get_collector_config()
    scanner_config = config.get_scanner_config()
    db_config = config.get_database_config()

    database = Database(db_config)
    collector = Collector(collector_config, database)
    scanner = Scanner(scanner_config, database)
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

def collect():
    # TODO: wrapper function of Collector.run()
    # lock for single collector instance
    print("Collecting data...")

def process(modules):
    # TODO: wrapper function to run modules
    # lock for each module, so that each module run single instance
    print(f"Processing modules: {', '.join(modules)}")

def cli():
    parser = argparse.ArgumentParser(description="MoveLook system, collect log data and process them")

    # read config
    parser.add_argument('-c', '--config', type=str, help='Path to the config file', required=True)

    # collect log data
    parser.add_argument('--collect', action='store_true', help='Collect data')

    # process log data
    parser.add_argument('--process', nargs='+', help='Process specified modules')

    args = parser.parse_args()

    if not os.path.exists(args.config):
        print(f"Config file {args.config} does not exist")
        sys.exit(1)

    if args.collect:
        collect()

    if args.process:
        process(args.process)

    # check if no command provided
    tmp_args = vars(args).copy()
    tmp_args.pop('config')
    for i in tmp_args:
        if (tmp_args[i]):
            return
    print(" no command specified")


if __name__ == "__main__":
    cli()

