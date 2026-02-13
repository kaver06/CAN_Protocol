import can

def init_can():
    return can.interface.Bus(
        interface="udp_multicast",
        channel="224.1.1.1",
        port=5000,
        receive_own_messages=False
    )

def send_rpm(bus, rpm_raw):
    msg = can.Message(
        arbitration_id=0x080,
        data=bytes([rpm_raw & 0xFF, (rpm_raw >> 8) & 0xFF]),
        is_extended_id=False
    )
    bus.send(msg)
