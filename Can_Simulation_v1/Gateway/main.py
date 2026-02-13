import can
import time


high_speed_bus = can.interface.Bus('vcan0', interface='socketcan')
low_speed_bus = can.interface.Bus('vcan1', interface='socketcan')

last_sent_time = 0

print("Gateway is live! Monitoring vcan0 (High Speed) and vcan1 (Low Speed)...")

while True:
    msg = high_speed_bus.recv() 
    

    if msg.arbitration_id == 0x123:
        current_time = time.time()
        

        if (current_time - last_sent_time) > 0.1: 
            low_speed_bus.send(msg)
            last_sent_time = current_time
            print(f">>> Forwarded Engine Temp to Low Speed Bus: {msg.data.hex()}")
