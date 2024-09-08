import threading
import time
import traceback

class Timer(object):
    def __init__(self, interval):
        self._timer = None
        self.interval = interval
        self.is_running = False
        self.next_call = time.time()
        # self.start()
        # self.function(*self.args, **self.kwargs)

    def _run(self):
        self.is_running = False
        self.start()
        if self.function is not None:
            self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self.next_call += self.interval
            self._timer = threading.Timer(self.next_call - time.time(), self._run)
            self._timer.start()
            self.is_running = True

    def set_function(self, function, *args, **kwargs):
        self.function = function
        self.args = args
        self.kwargs = kwargs

    def stop(self):
        if self.is_running:
            self._timer.cancel()
            self.is_running = False

    # def every(self):
    #       next_time = time.time() + self.interval
    #       while True:
    #           time.sleep(max(0, next_time - time.time()))
    #           try:
    #               self.function(*self.args, **self.kwargs)
    #           except Exception:
    #               traceback.print_exc()
    #               # in production code you might want to have this instead of course:
    #               # logger.exception("Problem while executing repetitive task.")
    #           # skip tasks if we are behind schedule:
    #           next_time += (time.time() - next_time) // self.interval * self.interval + self.interval
    #
    # def repeatEvery(self):
    #       threading.Thread(target=lambda: self.every()).start()
