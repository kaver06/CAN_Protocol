# core/dispatcher.py
import threading
import queue

class CANDispatcher:
    def __init__(self, can_bus):
        self.can = can_bus
        self.subscribers = []
        self.running = True

        self.thread = threading.Thread(
            target=self._rx_loop,
            daemon=True
        )
        self.thread.start()

    def subscribe(self):

        q = queue.Queue()
        self.subscribers.append(q)
        return q

    def _rx_loop(self):
       # print("[DISPATCHER] RX thread started")

        while self.running:
            msg = self.can.recv()
            if msg is None:
                continue

            #print(f"[DISPATCHER] RX {hex(msg.arbitration_id)} {list(msg.data)}")

            for q in self.subscribers:
                q.put(msg)

