import can

def init_can():
    return can.interface.Bus(
        interface="udp_multicast",
        channel="224.1.1.1",
        port=5000,
        receive_own_messages=False
    )

def send_diag(bus, counter):
    msg = can.Message(
        arbitration_id=0x300,
        data=[counter & 0xFF],
        is_extended_id=False
    )
    bus.send(msg)
