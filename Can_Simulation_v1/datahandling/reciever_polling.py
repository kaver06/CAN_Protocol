import can
import time
import numpy as np

bus = can.interface.Bus(channel='vcan0', interface='socketcan')

latencies = []
expected_seq = None
dropped = 0
processed = 0

print("Polling receiver started")


def burn_cpu(us):
    end = time.perf_counter() + us / 1_000_000
    while time.perf_counter() < end:
        pass
while True:
    msg = bus.recv(timeout=0.001)  # polling window

    if msg is None:
        continue

    # simulate decode + logic cost
    burn_cpu(500)
    seq = int.from_bytes(msg.data[:4], 'little')

    if expected_seq is None:
        expected_seq = seq
    elif seq != expected_seq:
        dropped += (seq - expected_seq)

    expected_seq = seq + 1

    latencies.append(time.time() - msg.timestamp)
    processed += 1

    if processed % 1000 == 0:
        print(
            f"POLL  "
            f"dropped={dropped}"
        )
        latencies.clear()

