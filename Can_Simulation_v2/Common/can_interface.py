import can

def init_can(channel="vcan0", bitrate=500000):
    return can.interface.Bus(
        interface="socketcan",
        channel=channel,
        bitrate=bitrate
    )
