import can
import cantools


db = cantools.database.load_file('vehicle.dbc')


bus = can.interface.Bus(interface='socketcan', channel='vcan0')

print("RECEIVER: Dashboard ON. Waiting for data...")

try:
    while True:

        msg = bus.recv() 
        
        if msg.arbitration_id == 100:
            
            decoded_data = db.decode_message(msg.arbitration_id, msg.data)
            

            temp = decoded_data['Temperature']
            volt = decoded_data['Voltage']
            rpm = decoded_data['RPM']
            

            print(f"DASHBOARD: temperature {temp} C  |  voltage {volt:.1f} V  |  speed {rpm} RPM")
            

            hex_str = ' '.join(f'{x:02X}' for x in msg.data)
            print(f"   (Raw Hex: {hex_str})")

except KeyboardInterrupt:
    print("\nRECEIVER: Dashboard OFF.")
