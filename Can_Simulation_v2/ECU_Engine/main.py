import can
import cantools

from Common.scheduler import PeriodicTask
from Common.can_interface import init_can
from Common.message_ids import ENGINE_DATA

from Common.dbc_loader import load_dbc
dbc = load_dbc()

bus = init_can()

task_1ms = PeriodicTask(10)

rpm_raw = 1000

print("[ECU_ENGINE] Started")

try:
    while True:

        # Encode using DBC
        data = dbc.encode_message("EngineData", {"RPM": rpm_raw})

        msg = can.Message(
            arbitration_id=ENGINE_DATA,
            data=data,
            is_extended_id=False
        )

        bus.send(msg)

        rpm_raw += 10
        if rpm_raw > 4000:
            rpm_raw = 1000

        task_1ms.wait()

except KeyboardInterrupt:
    bus.shutdown()
