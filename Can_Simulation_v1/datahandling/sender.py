import can 
import time 


bus = can.interface.Bus(channel='vcan0', interface='socketcan') 
counter = 0 
msg = can.Message(
	arbitration_id=0x123,
	data=[0]*8, 
	is_extended_id=False 
) 
print("Sender running (no sleep)...") 
TARGET_HZ = 6000 
PERIOD = 1.0 / TARGET_HZ 


while True: 
	msg.timestamp = time.time() 
	msg.data = counter.to_bytes(4,'little') + b'\x00'*4 
	counter += 1 				
	bus.send(msg) 
	time.sleep(PERIOD)
