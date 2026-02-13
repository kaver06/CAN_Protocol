from can_if import init_can, send_diag
import time

bus = init_can()
counter = 0

print("[ECU_DIAGNOSTICS] Started (ID=0x700)")
print("Sending diagnostic bursts every 0.2 seconds")

try:
    while True:

        # Burst of messages
        for _ in range(10):
            send_diag(bus, counter)
            counter += 1
            time.sleep(0.01)  # fast burst

        time.sleep(0.01)  # idle gap

except KeyboardInterrupt:
    bus.shutdown()
