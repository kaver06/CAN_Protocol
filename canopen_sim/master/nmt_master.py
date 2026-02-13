# master/nmt_master.py
import time
from core.nmt import NMTCommand


class NMTMaster:
    def __init__(self, can_bus):
        self.can = can_bus

    def send(self, command, node_id=0):
        self.can.send(
            0x000,
            [command.value, node_id]
        )
        print(f"[MASTER] {command.name} → Node {node_id}")

    def start_all(self):
        self.send(NMTCommand.START, 0)

    def stop_all(self):
        self.send(NMTCommand.STOP, 0)

    def preop_all(self):
        self.send(NMTCommand.ENTER_PRE_OP, 0)
