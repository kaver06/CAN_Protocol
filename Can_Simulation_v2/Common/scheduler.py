import time

class PeriodicTask:
    def __init__(self, period_ms):
        self.period = period_ms / 1000.0
        self.next_time = time.monotonic()

    def wait(self):
        self.next_time += self.period
        sleep_time = self.next_time - time.monotonic()
        if sleep_time > 0:
            time.sleep(sleep_time)
