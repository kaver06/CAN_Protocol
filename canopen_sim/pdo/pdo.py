# pdo/pdo.py
import struct
import threading
import time
from core.nmt import NMTState

class RPDO1:
    def __init__(self, node_id, od, nmt_state_ref):
        self.node_id = node_id
        self.od = od
        self.nmt_state_ref = nmt_state_ref

        # RPDO1 COB-ID: 0x200 + NodeID
        self.cob_id = 0x200 + node_id

    def process(self, cob_id, data):
        # 1. COB-ID Filter (Redundant if caller checks, but safe to have)
        if cob_id != self.cob_id:
            return

        # 2. NMT Gating
        # RPDO is valid ONLY in OPERATIONAL state
        if self.nmt_state_ref() != NMTState.OPERATIONAL:
            return

        # 3. Data Length Check (We expect 2 bytes for UNSIGNED16)
        if len(data) < 2:
            return

        # 4. Parse and Write to OD
        # Mapping is currently hardcoded: Bytes 0-1 -> OD 0x2002 (Target Speed)
        target_speed = struct.unpack('<H', bytes(data[0:2]))[0]
        
        # Update the Source of Truth
        print(f"[RPDO {self.node_id}] Received Target Speed: {target_speed}")
        self.od.write(0x2002, 0x00, target_speed)
        
class TPDO1:
    def __init__(self, node_id, od, can_bus, nmt_state_ref):

        self.node_id = node_id
        self.od = od
        self.can = can_bus

        # Reference (callable) to current NMT state
        self.nmt_state_ref = nmt_state_ref

        # CANopen-defined COB-ID for TPDO1
        self.cob_id = 0x180 + node_id

        self.enabled = True
        self.period = 0.1  # 100 ms

        # Start TPDO task
        self.thread = threading.Thread(
            target=self._task,
            daemon=True
        )
        self.thread.start()

    def _task(self):

        while self.enabled:
            if self.nmt_state_ref() != NMTState.OPERATIONAL:
                time.sleep(0.01)
                continue

            speed = self.od.read(0x2000, 0x00)
            current = self.od.read(0x2001, 0x00)

            payload = struct.pack("<HH", speed, current)
            self.can.send(self.cob_id, list(payload))

            time.sleep(self.period)
