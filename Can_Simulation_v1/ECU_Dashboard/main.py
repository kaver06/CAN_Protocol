import can_if
import time
import sys
import csv
import os
import can
import cantools

bus = can_if.init_can()
dbc = cantools.database.load_file("vehicle.dbc")

Enable_CSV_Log = True
Enable_ASC_Log = False
Enable_TRC_Log = False
Enable_BLF_Log = False

frame_count = 0

if Enable_CSV_Log:
    LOG_FILE = "Log_files/can_log.csv"

    file_exists = os.path.isfile(LOG_FILE)
    csv_file = open(LOG_FILE, mode="a", newline="")
    csv_writer = csv.writer(csv_file)

    if not file_exists:
        csv_writer.writerow([
            "timestamp",
            "arbitration_id",
            "dlc",
            "data_0", "data_1", "data_2", "data_3",
            "data_4", "data_5", "data_6", "data_7"
        ])


if Enable_ASC_Log:
    LOG_FILE = "Log_files/can_log.asc"
    asc_file = open(LOG_FILE, "a")

    if asc_file.tell() == 0:
        asc_file.write(f"date {time.strftime('%Y-%m-%d')}\n")
        asc_file.write("base hex  timestamps relative\n")
        asc_file.write("internal events logged\n\n")


if Enable_TRC_Log:
    trc_logger = can.Logger("Log_files/can_log.trc")

if Enable_BLF_Log:
    blf_writer = can.io.BLFWriter("Log_files/can_log.blf")


state = {
    "rpm": None,
    "speed": None,
    "temp": None,
    "diag": None,
    "last_rx": {
        "rpm": None,
        "speed": None,
        "temp": None,
        "diag": None,
    }
}

DISPLAY_PERIOD = 0.001

print("[ECU_DASHBOARD] Started")
dashboard_start_time = time.monotonic()

def decode_message(msg):
    now = time.monotonic()

    try:
        decoded = dbc.decode_message(msg.arbitration_id, msg.data)
    except KeyError:
        return

    for signal, value in decoded.items():

        if signal == "RPM":
            state["rpm"] = int(value)
            state["last_rx"]["rpm"] = now

        elif signal == "SPEED":
            state["speed"] = int(value)
            state["last_rx"]["speed"] = now

        elif signal == "TEMP":
            state["temp"] = int(value)
            state["last_rx"]["temp"] = now

        elif signal == "DIAG_CNT":
            state["diag"] = int(value)
            state["last_rx"]["diag"] = now

def age(key):
    t = state["last_rx"][key]
    if t is None:
        return "STALE"
    return f"{(time.monotonic() - t)*1000:.0f} ms"

def draw_dashboard():
    sys.stdout.write("\033[H\033[J")
    sys.stdout.write(
        "==== VEHICLE DASHBOARD ====\n\n"
        f"RPM          : {state['rpm']}   ({age('rpm')})\n"
        f"Speed        : {state['speed']}   ({age('speed')})\n"
        f"Temperature  : {state['diag']} °C   ({age('diag')})\n"
        f"Diagnostics  : {state['temp']}   ({age('temp')})\n"
        "\n==========   =================\n"
    )
    sys.stdout.flush()

# Initial draw
last_draw = time.monotonic()

try:
    while True:
        msg = bus.recv(timeout=0.01)
        if msg:
            frame_count += 1
            if Enable_CSV_Log:
                data = list(msg.data)
                data += [""] * (8 - len(data))  # pad to 8 bytes

                csv_writer.writerow([
                    time.monotonic() - dashboard_start_time,
                    f"0x{msg.arbitration_id:X}",
                    msg.dlc,
                    *data
                ])
            if Enable_ASC_Log:
                timestamp = time.monotonic() - dashboard_start_time
                can_id = f"{msg.arbitration_id:03X}"
                dlc = msg.dlc
                data_bytes = " ".join(f"{b:02X}" for b in msg.data)

                asc_line = (
                    f"{timestamp:.9f} "
                    f"1 "
                    f"{can_id} "
                    f"Rx "
                    f"d "
                    f"{dlc} "
                    f"{data_bytes}\n"
                )

                asc_file.write(asc_line)

            if Enable_TRC_Log:
                trc_logger.on_message_received(msg)

            if Enable_BLF_Log:
                blf_writer.on_message_received(msg)
                if frame_count % 1000 == 0:
                    blf_writer.file.flush()

            decode_message(msg)

        now = time.monotonic()
        if now - last_draw >= DISPLAY_PERIOD:
            draw_dashboard()
            last_draw = now

except KeyboardInterrupt:
    bus.shutdown()
    if Enable_CSV_Log:
        csv_file.close()
    if Enable_ASC_Log:
        asc_file.close()
    if Enable_TRC_Log:
        trc_logger.stop()
    if Enable_BLF_Log:
        blf_writer.stop()
