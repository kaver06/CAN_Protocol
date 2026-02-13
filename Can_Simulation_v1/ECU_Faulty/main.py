import can_if
import time

bus = can_if.init_can()

print("[ECU_FAULTY] Started")
print("ID=0x000 | RPM=0 | ")
rpm = 0
try:
    while True:
        can_if.send_faulty_rpm(bus,rpm)
        time.sleep(0)

except KeyboardInterrupt:
    bus.shutdown()
