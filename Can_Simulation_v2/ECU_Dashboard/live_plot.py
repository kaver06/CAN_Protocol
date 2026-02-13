import time
import threading
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque

from Common.can_interface import init_can
from Common.dbc_loader import load_dbc

from Common.metrics import CANMetrics

metrics = CANMetrics(window_seconds=1.0)

WINDOW_SECONDS = 10
FPS = 60
INTERVAL_MS = 1000 / FPS  # ~16ms for 60fps

bus = init_can()
dbc = load_dbc()

print("[LIVE PLOT] Started")

start_time = time.monotonic()


rpm_time = deque(maxlen=2000)
rpm_data = deque(maxlen=2000)

speed_time = deque(maxlen=2000)
speed_data = deque(maxlen=2000)

temp_time = deque(maxlen=2000)
temp_data = deque(maxlen=2000)

# Flag to stop the background thread safely
running = True



def read_can_data():
    global running
    while running:

        msg = bus.recv(timeout=1.0)

        if msg:
            now = time.monotonic()
            current_time = now - start_time

            try:
                decoded = dbc.decode_message(msg.arbitration_id, msg.data)
            except KeyError:
                continue

            # Append data immediately
            if "RPM" in decoded:
                rpm_time.append(current_time)
                rpm_data.append(decoded["RPM"])
                metrics.update("RPM")

            if "SPEED" in decoded:
                speed_time.append(current_time)
                speed_data.append(decoded["SPEED"])
                metrics.update("SPEED")

            if "TEMP" in decoded:
                temp_time.append(current_time)
                temp_data.append(decoded["TEMP"])
                metrics.update("TEMP")

# Start the data thread
data_thread = threading.Thread(target=read_can_data, daemon=True)
data_thread.start()


plt.style.use("dark_background")

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 8))
plt.subplots_adjust(hspace=0.3)

# RPM Plot
line_rpm, = ax1.plot([], [], color="#ff3b30", linewidth=2, label="RPM")  # Smoother red
ax1.set_title("Engine RPM", fontsize=14, fontweight='bold')
ax1.set_ylabel("RPM")
ax1.set_ylim(0, 4500)
ax1.set_xlim(0, WINDOW_SECONDS)
ax1.grid(True, alpha=0.2, linestyle='--')
ax1.legend(loc='upper right')

# Speed + Temp Plot
line_speed, = ax2.plot([], [], color="#00e5ff", linewidth=2, label="Speed")  # Neon cyan
line_temp, = ax2.plot([], [], color="#ff9100", linewidth=2, label="Temp")  # Neon orange
ax2.set_title("Speed & Temperature", fontsize=14, fontweight='bold')
ax2.set_xlabel("Time (s)")
ax2.set_ylabel("Value")
ax2.set_ylim(0, 150)
ax2.set_xlim(0, WINDOW_SECONDS)
ax2.grid(True, alpha=0.2, linestyle='--')
ax2.legend(loc='upper right')

def update(frame):
    now = time.monotonic()
    current_time = now - start_time


    if current_time > WINDOW_SECONDS:
        limit_low = current_time - WINDOW_SECONDS
        limit_high = current_time
        ax1.set_xlim(limit_low, limit_high)
        ax2.set_xlim(limit_low, limit_high)


    if len(rpm_time) > 1:
        line_rpm.set_data(rpm_time, rpm_data)

    if len(speed_time) > 1:
        line_speed.set_data(speed_time, speed_data)

    if len(temp_time) > 1:
        line_temp.set_data(temp_time, temp_data)

    rpm_hz = metrics.get_frequency("RPM")
    speed_hz = metrics.get_frequency("SPEED")
    temp_hz = metrics.get_frequency("TEMP")
    total_hz = metrics.get_total_frequency()

    # ---- Bus Load Calculation ----
    CAN_BITRATE = 500_000
    BITS_PER_FRAME = 120

    bus_load = (total_hz * BITS_PER_FRAME) / CAN_BITRATE * 100

    # ---- Timeout Detection ----
    rpm_timeout = metrics.is_timeout("RPM", 0.1)
    speed_timeout = metrics.is_timeout("SPEED", 0.1)
    temp_timeout = metrics.is_timeout("TEMP", 0.2)

    rpm_status = "TIMEOUT" if rpm_timeout else f"{rpm_hz:.1f} Hz"
    speed_status = "TIMEOUT" if speed_timeout else f"{speed_hz:.1f} Hz"
    temp_status = "TIMEOUT" if temp_timeout else f"{temp_hz:.1f} Hz"

    ax1.set_title(f"Engine RPM | {rpm_status}")

    ax2.set_title(
        f"Speed & Temp | "
        f"Speed: {speed_status} | "
        f"Temp: {temp_status} | "
        f"Bus: {total_hz:.1f} Hz | "
        f"Load: {bus_load:.2f}%"
    )

    return line_rpm, line_speed, line_temp
ani = animation.FuncAnimation(fig, update, interval=INTERVAL_MS, blit=False, cache_frame_data=False)

try:
    plt.show()
except KeyboardInterrupt:
    print("\nStopping plot...")
finally:
    running = False

    print("Done.")