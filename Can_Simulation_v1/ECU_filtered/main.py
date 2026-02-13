import can_if
import time

bus = can_if.init_can()

bus.set_filters([
    {"can_id": 0x080, "can_mask": 0x7FF, "extended": False},
    {"can_id": 0x100, "can_mask": 0x7FF, "extended": False},
])

print("[FILTERED DASHBOARD] Started")
print("Accepting only:")
print("  Engine   : 0x080 (RPM)")
print("  Chassis  : 0x100 (Speed)\n")

try:
    while True:
        msg = bus.recv(timeout=1)

        if msg:
            print(
                f"RX  "
                f"ID=0x{msg.arbitration_id:03X}  "
                f"DATA={list(msg.data)}"
            )

except KeyboardInterrupt:
    bus.shutdown()
