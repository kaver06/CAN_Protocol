import csv
import time
import os
from pathlib import Path

class CSVLogger:
    def __init__(self, filename):
        filepath = Path(filename)

        # Create directory if it does not exist
        filepath.parent.mkdir(parents=True, exist_ok=True)

        file_exists = filepath.exists()

        self.file = open(filepath, "a", newline="")
        self.writer = csv.writer(self.file)

        if not file_exists:
            self.writer.writerow([
                "timestamp",
                "arbitration_id",
                "dlc",
                "data_0", "data_1", "data_2", "data_3",
                "data_4", "data_5", "data_6", "data_7"
            ])

    def log(self, msg, start_time):
        data = list(msg.data)
        data += [""] * (8 - len(data))

        self.writer.writerow([
            time.monotonic() - start_time,
            f"0x{msg.arbitration_id:X}",
            msg.dlc,
            *data
        ])

    def close(self):
        self.file.close()
