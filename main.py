# main program run here

from getData.processor import Processor
import sys
from getData.utils.repeatTimer import RepeatedTimer
from rconfig import Config

config = Config(sys.argv[1]).get_all()

def init_log_reading():
    # read the config file
    p = Processor(config)
    p.es.connect()
    # print config interval
    print(f"Interval: {p.config['interval']}")
    return p

# TODO: read large file
# TODO: count time using for inserting data
# TODO: connect to cuhk cluster
def main(p):
    interval = p.config['interval']
    rt = RepeatedTimer(interval, p.process)
    try:
        while True:
            print()
            print('Enter command (q:quit, c:clear database, r:run processor, h:help)')
            command = input()
            if command == 'q':
                rt.stop()
                break
            # clear the database
            elif command == 'c':
                p.es.clear_database()
                p = init_log_reading()
            elif command == 'r':
                print('Running processor')
                rt.start()
            # stop the processor
            elif command == 's':
                print('Stop processor')
                rt.stop()
            elif command == 'h':
                print('q:quit')
                print('c:clear database')
                print('r:run processor')
                print('s:stop processor')

    except KeyboardInterrupt:
        print('Interrupted')
        rt.stop()
    finally:
        rt.stop()

# def main(p):
#     interval = p.config['interval']
#     rt = RepeatedTimer(interval, p.print_marker)
#     rt.start()
#     time.sleep(10)
#     rt.stop()



if __name__ == '__main__':
    processor = init_log_reading()
    main(processor)
