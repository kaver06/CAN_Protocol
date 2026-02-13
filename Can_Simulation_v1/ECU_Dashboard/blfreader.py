import can
import csv

BLF_FILE = "Log_files/can_log.blf"
CSV_FILE = "Log_files/canlog_blftocsv.csv"

print(f"[BLF → CSV] Reading {BLF_FILE}")
print(f"[BLF → CSV] Writing {CSV_FILE}")

reader = can.LogReader(BLF_FILE)

with open(CSV_FILE, mode="w", newline="") as f:
    writer = csv.writer(f)

    # CSV header
    writer.writerow([
        "timestamp",
        "arbitration_id",
        "dlc",
        "data_0", "data_1", "data_2", "data_3",
        "data_4", "data_5", "data_6", "data_7",
        "is_rx",
        "is_extended_id",
        "is_remote_frame",
        "is_error_frame",
        "is_fd",
        "bitrate_switch",
        "error_state_indicator",
        "channel"
    ])

    frame_count = 0

    for msg in reader:
        frame_count += 1

        # Payload (pad to 8 bytes for CSV consistency)
        data = list(msg.data)
        data += [""] * (8 - len(data))

        writer.writerow([
            msg.timestamp,
            f"0x{msg.arbitration_id:X}",
            msg.dlc,
            *data,
            msg.is_rx,
            msg.is_extended_id,
            msg.is_remote_frame,
            msg.is_error_frame,
            getattr(msg, "is_fd", None),
            getattr(msg, "bitrate_switch", None),
            getattr(msg, "error_state_indicator", None),
            msg.channel
        ])

print(f"[BLF → CSV] Done. Frames converted: {frame_count}")
