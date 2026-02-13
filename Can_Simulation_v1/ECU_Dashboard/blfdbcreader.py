import can
import cantools
import csv

# ================== CONFIG ==================
BLF_FILE = "Log_files/can_log.blf"
DBC_FILE = "vehicle.dbc"
CSV_FILE = ("Log_files/canlog_blfdbccsv.csv")
# ============================================

print("[INFO] Loading DBC...")
db = cantools.database.load_file(DBC_FILE)

print(f"[INFO] Reading BLF : {BLF_FILE}")
print(f"[INFO] Writing CSV: {CSV_FILE}")

reader = can.LogReader(BLF_FILE)

with open(CSV_FILE, mode="w", newline="") as f:
    writer = csv.writer(f)

    # Signal-level CSV header
    writer.writerow([
        "timestamp",
        "arbitration_id",
        "message_name",
        "signal_name",
        "value",
        "unit",
        "channel",
        "is_extended_id",
        "direction"
    ])

    frame_count = 0
    decoded_count = 0
    skipped_count = 0

    for msg in reader:
        frame_count += 1

        # Skip non-data frames early
        if msg.is_error_frame or msg.is_remote_frame:
            skipped_count += 1
            continue

        try:
            message = db.get_message_by_frame_id(msg.arbitration_id)
            decoded_signals = message.decode(msg.data)
        except Exception:
            # Frame not defined in DBC (normal in real logs)
            skipped_count += 1
            continue

        for signal in message.signals:
            writer.writerow([
                msg.timestamp,
                msg.arbitration_id,
                message.name,
                signal.name,
                decoded_signals.get(signal.name),
                signal.unit or "",
                msg.channel,
                msg.is_extended_id,
                "rx"   # BLF is receive-side unless proven otherwise
            ])
            decoded_count += 1

print("\n[INFO] Conversion complete")
print(f"[INFO] Frames read      : {frame_count}")
print(f"[INFO] Signals decoded  : {decoded_count}")
print(f"[INFO] Frames skipped   : {skipped_count}")
