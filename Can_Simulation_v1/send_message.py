import can

bus = can.interface.Bus(
    interface="virtual",
    channel=0,
    receive_own_messages=True
)

msg = can.Message(
    arbitration_id=0x123,
    data=[0x11, 0x22, 0x33],
)

bus.send(msg)
rx = bus.recv(timeout=1)
bus.send(msg)
print("Sent:", msg)

rx = bus.recv(timeout=1)
if rx:
    print("Received:", rx)
else:
    print("No message received")
bus.shutdown()
