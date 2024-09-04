# main program run here

from processor import Processor
from utils.repeatTimer import RepeatedTimer
from utils.database import Database
from config import Config

import sys

config = Config(sys.argv[1])
reader_config = config.get_reader_config()
print(config)

def init_log_reading():
    # read the config file
    read_log_db = Database(config.get_db_info())
    read_log_db.connect()
    p = Processor(reader_config, read_log_db)
    # print config interval
    print(f"Interval: {p.config['interval']}")
    return p

# TODO: integrate a demo of warning system

# TODO: can hot reload the config file
# new method in config.py: self.reload_config()
# simply read the config file again

# TODO: make a plugin system for warning
def main(p):
    log_reading_interval = reader_config['interval']
    log_reading_timer = RepeatedTimer(log_reading_interval, p.process)
    # rt.function()
    try:
        while True:
            print('Enter command (h for help):')
            print('Command:', end=' ')
            command = input()
            if command == 'q':
                log_reading_timer.stop()
                break
            # clear the database
            elif command == 'c':
                p.es.clear_database()
                p = init_log_reading()
            elif command == 'r':
                print('Running processor')
                log_reading_timer.start()
            # stop the processor
            elif command == 's':
                print('Stop processor')
                log_reading_timer.stop()
            elif command == 'h':
                print('q:quit')
                print('c:clear database')
                print('r:run processor')
                print('s:stop processor')

    except KeyboardInterrupt:
        print('Interrupted')
        log_reading_timer.stop()
    finally:
        log_reading_timer.stop()

# def main(p):
#     interval = p.config['interval']
#     rt = RepeatedTimer(interval, p.print_marker)
#     rt.start()
#     time.sleep(10)
#     rt.stop()



if __name__ == '__main__':
    processor = init_log_reading()
    main(processor)
