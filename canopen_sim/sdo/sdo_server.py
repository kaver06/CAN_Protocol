# sdo/sdo_server.py
class SDOServer:
    def __init__(self, node_id, od, can_bus):
        self.node_id = node_id
        self.od = od
        self.can = can_bus

        self.rx_cob_id = 0x600 + node_id
        self.tx_cob_id = 0x580 + node_id

    def handle(self, msg):
        if msg.arbitration_id != self.rx_cob_id:
            return

        cs = msg.data[0]
        index = msg.data[1] | (msg.data[2] << 8)
        subindex = msg.data[3]

        # -------- READ --------
        if cs == 0x40:
            value = self.od.read(index, subindex)

            resp = [
                0x43,
                msg.data[1],
                msg.data[2],
                subindex,
                value & 0xFF,
                (value >> 8) & 0xFF,
                (value >> 16) & 0xFF,
                (value >> 24) & 0xFF
            ]
            self.can.send(self.tx_cob_id, resp)

        # -------- WRITE --------
        elif cs in (0x2F, 0x2B, 0x27, 0x23):
            value = (
                msg.data[4]
                | (msg.data[5] << 8)
                | (msg.data[6] << 16)
                | (msg.data[7] << 24)
            )
            self.od.write(index, subindex, value)

            resp = [
                0x60,
                msg.data[1],
                msg.data[2],
                subindex,
                0, 0, 0, 0
            ]
            self.can.send(self.tx_cob_id, resp)
