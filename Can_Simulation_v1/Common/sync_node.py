import socket
import time
import struct

MCAST_GRP = "224.1.1.50"
PORT = 9000

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)

print("[SYNC] Started (multicast)")

try:
    while True:
        time.sleep(1)
        t = time.monotonic()
        sock.sendto(b"TICK", (MCAST_GRP, PORT))
        print(f"[SYNC] Tick sent @ {t:.6f}")

except KeyboardInterrupt:
    sock.close()
