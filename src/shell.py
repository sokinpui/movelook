import mytest
import importlib
from datetime import datetime

# can you write a simple shell for me?
# R to reload the test() function
# r to run the test() function

def run_test():
    print("====================================")
    print(f'Running test() at {datetime.now()}')
    print()
    try:
        mytest.test()
    except Exception as e:
        print(f'An error occurred: {e}')
    print()
    print("====================================")
    print()

def reload_test():
    importlib.reload(mytest)
    print("====================================")
    print('=========Reloaded mytest.py=========')
    print("====================================")
    print()

def main():
    while True:
        cmd = input('Enter command: ')
        if cmd == 'R':
            reload_test()
        elif cmd == 'r':
            run_test()
        elif cmd == "rr":
            reload_test()
            run_test()
        elif cmd == 'q':
            print('Exiting...')
            break
        else:
            print('Invalid command!')

if __name__ == '__main__':
    main()

