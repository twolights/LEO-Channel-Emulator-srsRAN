import math
from typing import Callable

from PyQt5 import QtCore
import threading
import time


class PreciseTimer:
    @staticmethod
    def _thread_handler(timer):
        sleep_interval = math.floor(timer.interval / 2)
        last_time = time.time_ns()

        while timer.is_running:
            current_time = time.time_ns()
            if current_time - last_time >= timer.interval:
                last_time = current_time
                timer.callback()
            time.sleep(sleep_interval * 1e-9)

    callback: Callable
    interval: float = 1000  # nano seconds
    is_running: bool = False
    thread: threading.Thread

    def start(self, interval: float, callback: Callable):
        self.is_running = True
        self.interval = interval
        self.callback = callback
        self.thread = threading.Thread(target=self._thread_handler, args=(self,))
        self.thread.start()

    def stop(self):
        self.is_running = False
        self.thread.join()

