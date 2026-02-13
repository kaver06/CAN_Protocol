import can

def init_can():
    return can.interface.Bus(
        interface="udp_multicast",
        channel="224.1.1.1",
        port=5000,
        receive_own_messages=False
    )

def send_speed(bus, speed_raw):
    msg = can.Message(
        arbitration_id=0x100,   # LOWER priority than 0x100
        data=bytes([speed_raw & 0xFF, (speed_raw >> 8) & 0xFF]),
        is_extended_id=False
    )
    bus.send(msg)
