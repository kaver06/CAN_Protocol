import can
import cantools

from Common.scheduler import PeriodicTask
from Common.can_interface import init_can
from Common.message_ids import BODY_DATA

from Common.dbc_loader import load_dbc
dbc = load_dbc()


bus = init_can()

task_100ms = PeriodicTask(10)

raw_temp = 25

print("[ECU_BODY] Started")

try:
    while True:

        data = dbc.encode_message("BodyData", {"TEMP": raw_temp})

        msg = can.Message(
            arbitration_id=BODY_DATA,
            data=data,
            is_extended_id=False
        )

        bus.send(msg)

        raw_temp += 1
        if raw_temp > 35:
            raw_temp = 25

        task_100ms.wait()

except KeyboardInterrupt:
    bus.shutdown()
