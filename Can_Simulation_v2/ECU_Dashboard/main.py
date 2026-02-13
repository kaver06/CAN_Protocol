import time
import sys
import can
import cantools

from Common.can_interface import init_can
from Common.logger import CSVLogger
from Common.dbc_loader import load_dbc
dbc = load_dbc()

DISPLAY_PERIOD = 0.1
ENABLE_CSV_LOG = True

bus = init_can()

print("[ECU_DASHBOARD] Started")

dashboard_start_time = time.monotonic()
last_draw = dashboard_start_time
last_fps_time = dashboard_start_time

frame_count = 0
fps = 0

logger = None
if ENABLE_CSV_LOG:
    logger = CSVLogger("Log_files/can_log.csv")

state = {
    "rpm": None,
    "speed": None,
    "temp": None,
    "last_rx": {
        "rpm": None,
        "speed": None,
        "temp": None,
    }
}

def decode_message(msg):
    now = time.monotonic()

    try:
        decoded = dbc.decode_message(msg.arbitration_id, msg.data)
    except KeyError:
        return

    for signal, value in decoded.items():
        if signal == "RPM":
            state["rpm"]    = int(value)
            state["last_rx"]["rpm"] = now
        elif signal == "SPEED":
            state["speed"] = int(value)
            state["last_rx"]["speed"] = now
        elif signal == "TEMP":
            state["temp"] = int(value)
            state["last_rx"]["temp"] = now


def age(key):
    t = state["last_rx"][key]
    if t is None:
        return "STALE"
    return f"{(time.monotonic() - t) * 1000:.0f} ms"


def draw_dashboard(current_fps):
    sys.stdout.write("\033[H\033[J")
    sys.stdout.write(
        "==== VEHICLE DASHBOARD ====\n\n"
        f"RPM          : {state['rpm']}   ({age('rpm')})\n"
        f"Speed        : {state['speed']}   ({age('speed')})\n"
        f"Temperature  : {state['temp']} °C   ({age('temp')})\n"
        f"\nFrame Rate   : {current_fps:.0f} FPS\n"
        "\n=============================\n"
    )
    sys.stdout.flush()

try:
    while True:
        msg = bus.recv(timeout=0.01)

        if msg:
            frame_count += 1

            if logger:
                logger.log(msg, dashboard_start_time)

            decode_message(msg)

        now = time.monotonic()

        if now - last_fps_time >= 1.0:
            fps = frame_count / (now - last_fps_time)
            frame_count = 0
            last_fps_time = now

        if now - last_draw >= DISPLAY_PERIOD:
            draw_dashboard(fps)
            last_draw = now

except KeyboardInterrupt:
    bus.shutdown()
    if logger:
        logger.close()
