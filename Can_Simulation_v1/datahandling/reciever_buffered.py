import can
import queue
import threading
import time


bus = can.interface.Bus(channel='vcan0', interface='socketcan')


QUEUE_SIZE = 1000
msg_queue = queue.Queue(maxsize=QUEUE_SIZE)


frames_received = 0
frames_dropped = 0


counter_lock = threading.Lock()

def burn_cpu(us):
    end = time.perf_counter() + us / 1_000_000
    while time.perf_counter() < end:
        pass
        
class MyListener(can.Listener):
    def on_message_received(self, msg):
        global frames_received, frames_dropped
        burn_cpu(250)
        try:
            msg_queue.put_nowait(msg)
        except queue.Full:
            with counter_lock:
                frames_dropped += 1
        with counter_lock:
            frames_received += 1
            if frames_received % 1000 == 0:
                print(f" BUFF dropped={frames_dropped}, Queue:{msg_queue.qsize()}")


listener = MyListener()


notifier = can.Notifier(bus, [listener])

try:
    print("Receiver running..")
    while True:
        try:
            msg = msg_queue.get(timeout=1)
            # optional: process msg here
        except queue.Empty:
            pass
except KeyboardInterrupt:
    notifier.stop()

