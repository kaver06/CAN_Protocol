import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from can_if import init_can, send_temperature
import Common.scheduler
import time

bus = init_can()
task_100ms = Common.scheduler.PeriodicTask(100)

temp = 25

print("[ECU_BODY] Started (ID=0x300)")

try:
    while True:
        t_attempt = time.monotonic()

        send_temperature(bus, temp)

        t_sent = time.monotonic()
        delay_us = (t_sent - t_attempt) * 1_000_000

        print(
            f"[Body TX] "
            f"attempt={t_attempt:.6f} "
            f"sent={t_sent:.6f} "
            f"delay={delay_us:.1f} µs"
        )

        temp += 1
        if temp > 35:
            temp = 25
        task_100ms.wait()

except KeyboardInterrupt:
    bus.shutdown()
