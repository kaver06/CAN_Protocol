import can
import time
import numpy as np

expected_seq = None
dropped = 0
processed = 0


def burn_cpu(us):
    end = time.perf_counter() + us / 1_000_000
    while time.perf_counter() < end:
        pass
class CallbackListener(can.Listener):
    def on_message_received(self, msg):
        global expected_seq, dropped, processed


        burn_cpu(250)
        seq = int.from_bytes(msg.data[:4], 'little')

        if expected_seq is None:
            expected_seq = seq
        elif seq != expected_seq:
            dropped += (seq - expected_seq)

        expected_seq = seq + 1

        processed += 1

        if processed % 1000 == 0:
            print(
                f"CALLB "

                f"dropped={dropped}"
            )


bus = can.interface.Bus(channel='vcan0', interface='socketcan')
listener = CallbackListener()
notifier = can.Notifier(bus, [listener])

print("Callback receiver started")

while True:
    time.sleep(1)

