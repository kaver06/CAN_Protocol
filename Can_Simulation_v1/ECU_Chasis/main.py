import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import can_if
import Common.scheduler
import time

bus = can_if.init_can()
task_10ms = Common.scheduler.PeriodicTask(10)

speed = 50

print("[ECU_CHASSIS] Started")

try:
    while True:
        t_attempt = time.monotonic()

        can_if.send_speed(bus, speed)

        t_sent = time.monotonic()
        delay_us = (t_sent - t_attempt) * 1_000_000

        print(
            f"[CHASSIS TX] "
            f"attempt={t_attempt:.6f} "
            f"sent={t_sent:.6f} "
            f"delay={delay_us:.1f} µs"
        )
        speed += 1
        if speed > 120:
            speed = 50
        task_10ms.wait()

except KeyboardInterrupt:
    bus.shutdown()
