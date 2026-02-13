import time

from bus.can_bus import CANBus
from core.dispatcher import CANDispatcher
from nodes.base_node import BaseNode
from master.nmt_master import NMTMaster


bus = CANBus("vcan0")
dispatcher = CANDispatcher(bus)

node1 = BaseNode(1, bus, dispatcher.subscribe())
node2 = BaseNode(2, bus, dispatcher.subscribe())

master = NMTMaster(bus)

START_DELAY = 5.0   # seconds
start_time = time.time()
started = False

try:
    while True:
        node1.process_can()
        node2.process_can()

        now = time.time()

        # Wait before starting network
        if not started and (now - start_time) >= START_DELAY:
            print("[MASTER] Network startup delay elapsed")
            master.start_all()
            started = True

        time.sleep(0.01)

except KeyboardInterrupt:
    print("Stopping simulation")
