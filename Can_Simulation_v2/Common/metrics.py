import time
from collections import defaultdict, deque

class CANMetrics:
    def __init__(self, window_seconds=1.0):
        self.window = window_seconds
        self.timestamps = defaultdict(deque)
        self.last_timestamp = {}
        self.total_frames = deque()

    def update(self, signal_name):
        now = time.monotonic()

        ts = self.timestamps[signal_name]
        ts.append(now)

        while ts and (now - ts[0]) > self.window:
            ts.popleft()

        self.last_timestamp[signal_name] = now

        self.total_frames.append(now)
        while self.total_frames and (now - self.total_frames[0]) > self.window:
            self.total_frames.popleft()

    def get_frequency(self, signal_name):
        return len(self.timestamps[signal_name]) / self.window

    def get_total_frequency(self):
        return len(self.total_frames) / self.window

    def is_timeout(self, signal_name, timeout_sec):
        now = time.monotonic()
        if signal_name not in self.last_timestamp:
            return True
        return (now - self.last_timestamp[signal_name]) > timeout_sec
