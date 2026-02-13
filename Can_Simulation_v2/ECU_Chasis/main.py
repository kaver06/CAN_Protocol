import can
import cantools

from Common.scheduler import PeriodicTask
from Common.can_interface import init_can
from Common.message_ids import CHASSIS_DATA

from Common.dbc_loader import load_dbc
dbc = load_dbc()


bus = init_can()

task_10ms = PeriodicTask(10)

raw_speed = 50

print("[ECU_CHASSIS] Started")

try:
    while True:

        data = dbc.encode_message("ChassisData", {"SPEED": raw_speed})

        msg = can.Message(
            arbitration_id=CHASSIS_DATA,
            data=data,
            is_extended_id=False
        )

        bus.send(msg)

        raw_speed += 1
        if raw_speed > 120:
            raw_speed = 50

        task_10ms.wait()

except KeyboardInterrupt:
    bus.shutdown()
