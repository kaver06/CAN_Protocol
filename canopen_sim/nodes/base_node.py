import time
import threading
from od.object_dictionary import ObjectDictionary
from od.od_entry import ODEntry
from od.datatypes import UNSIGNED8, UNSIGNED16, UNSIGNED32
from sdo.sdo_server import SDOServer
from core.nmt import NMTState, NMTCommand
# Import the new RPDO class
from pdo.pdo import TPDO1, RPDO1  

class BaseNode:
    def __init__(self, node_id, can_bus, rx_queue):
        self.node_id = node_id
        self.can = can_bus
        self.rx_queue = rx_queue

        self.nmt_state = NMTState.INITIALIZING
        self._running = True
        self.od = ObjectDictionary()

        self.sdo = SDOServer(self.node_id, self.od, self.can)

        # Standard Objects
        self.od.add(ODEntry(0x1000, 0x00, UNSIGNED32, 0x00000000, "ro"))
        self.od.add(ODEntry(0x1017, 0x00, UNSIGNED16, 1000, "rw"))
        self.od.add(ODEntry(0x1018, 0x00, UNSIGNED8, 4, "ro"))
        self.od.add(ODEntry(0x1018, 0x01, UNSIGNED32, 0x12345678, "ro"))
        self.od.add(ODEntry(0x1018, 0x02, UNSIGNED32, 0x00000001, "ro"))

        # -------------------------
        # APPLICATION PROCESS DATA
        # -------------------------
        self.od.add(ODEntry(0x2000, 0x00, UNSIGNED16, 100, "rw"))   # Actual Speed (TPDO)
        self.od.add(ODEntry(0x2001, 0x00, UNSIGNED16, 20, "rw"))    # Actual Current (TPDO)
        
        # [NEW] Target Speed (RPDO)
        # Default is 0. This is where RPDO writes.
        self.od.add(ODEntry(0x2002, 0x00, UNSIGNED16, 0, "rw")) 

        # Heartbeat Thread
        self.hb_thread = threading.Thread(target=self._heartbeat_task, daemon=True)
        self.hb_thread.start()

        print(f"[Node {self.node_id}] INITIALIZING")
        self.set_state(NMTState.PRE_OPERATIONAL)

        # Initialize TPDO
        self.tpdo1 = TPDO1(
            self.node_id, self.od, self.can, lambda: self.nmt_state
        )

        # [NEW] Initialize RPDO
        self.rpdo1 = RPDO1(
            self.node_id, self.od, lambda: self.nmt_state
        )

    # ... [Keep set_state, handle_nmt, _heartbeat_task exactly as they were] ...
    
    def set_state(self, new_state):
        self.nmt_state = new_state
        print(f"[Node {self.node_id}] → {new_state.name}")

    def handle_nmt(self, command):
        if command == NMTCommand.START:
            self.set_state(NMTState.OPERATIONAL)
        elif command == NMTCommand.STOP:
            self.set_state(NMTState.STOPPED)
        elif command == NMTCommand.ENTER_PRE_OP:
            self.set_state(NMTState.PRE_OPERATIONAL)
        elif command == NMTCommand.RESET_NODE:
            self.set_state(NMTState.INITIALIZING)
            time.sleep(0.1)
            self.set_state(NMTState.PRE_OPERATIONAL)
        elif command == NMTCommand.RESET_COMM:
            self.set_state(NMTState.PRE_OPERATIONAL)

    def _heartbeat_task(self):
        while self._running:
            hb_time_ms = self.od.read(0x1017, 0x00)
            hb_time_sec = hb_time_ms / 1000.0
            cob_id = 0x700 + self.node_id
            self.can.send(cob_id, [self.nmt_state.value])
            time.sleep(hb_time_sec)

    # -------------------------
    # CAN FRAME DISPATCH (UPDATED)
    # -------------------------
    def process_can(self):
        try:
            msg = self.rx_queue.get_nowait()
        except:
            return

        # 1. SDO Handling
        # (Assuming your SDO class handles COB-ID filtering internally)
        self.sdo.handle(msg)

        # 2. NMT Handling (COB-ID 0x000)
        if msg.arbitration_id == 0x000:
            if len(msg.data) >= 2:
                command = msg.data[0]
                target = msg.data[1]
                if target in (0, self.node_id):
                    self.handle_nmt(NMTCommand(command))

        # 3. [NEW] RPDO Handling
        if msg.arbitration_id == self.rpdo1.cob_id:
            self.rpdo1.process(msg.arbitration_id, msg.data)
