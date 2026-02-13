import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import can_if
import Common.scheduler
import time

bus = can_if.init_can()
task_10ms = Common.scheduler.PeriodicTask(1)

rpm = 1000

print("[ECU_ENGINE] Started")

try:
    while True:
        t_attempt = time.monotonic()

        can_if.send_rpm(bus, rpm)

        t_sent = time.monotonic()
        delay_us = (t_sent - t_attempt) * 1_000_000
        print(
            f"[ENGINE TX] "
            f"attempt={t_attempt:.6f} "
            f"sent={t_sent:.6f} "
            f"delay={delay_us:.1f} µs"
        )

        rpm += 10
        if rpm > 4000:
            rpm = 1000
        task_10ms.wait()

except KeyboardInterrupt:
    bus.shutdown()
