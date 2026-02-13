import can

def init_can():
    return can.interface.Bus(
        interface="udp_multicast",
        channel="224.1.1.1",
        port=5000,
        receive_own_messages=False
    )

def send_faulty_rpm(bus,rpm_raw):
    msg = can.Message(
        arbitration_id=0x000,   # HIGHEST priority (faulty)
        data=[rpm_raw & 0xFF, (rpm_raw >> 8) & 0xFF],              # 50 °C bogus temperature
        is_extended_id=False
    )
    bus.send(msg)
