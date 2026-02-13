# bus/can_bus.py
import can

class CANBus:
    def __init__(self, channel="vcan0"):
        self.bus = can.interface.Bus(
            channel=channel,
            bustype="socketcan",
            receive_own_messages = True
        )

    def send(self, can_id, data):
        msg = can.Message(
            arbitration_id=can_id,
            data=data,
            is_extended_id=False
        )
        self.bus.send(msg)

    def recv(self, timeout=0.1):
        return self.bus.recv(timeout)
