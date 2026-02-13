import can
import cantools
import time


db = cantools.database.load_file('vehicle.dbc')


engine_temp = 20.0  
battery_volt = 11.5 
engine_rpm = 800    


bus = can.interface.Bus(interface='socketcan', channel='vcan0')

print("SENDER: Engine Started. Transmitting on ID 0x100...")

try:
    while True:

        engine_temp += 0.5
        if engine_temp > 110: engine_temp = 80 
        battery_volt += 0.1
        if battery_volt > 14.5: battery_volt = 12.0 

        engine_rpm += 50
        if engine_rpm > 5000: engine_rpm = 800 

      
        message = db.get_message_by_name('EngineData')
        

        data_dict = {
            'Temperature': engine_temp,
            'Voltage': battery_volt,
            'RPM': engine_rpm
        }
        

        encoded_data = message.encode(data_dict)


        msg = can.Message(arbitration_id=message.frame_id, 
                          data=encoded_data, 
                          is_extended_id=False)
        
        bus.send(msg)
        
        print(f"Sent: Temp={engine_temp:.1f}C, Volt={battery_volt:.1f}V, RPM={engine_rpm}")
        
        time.sleep(1.0) 

except KeyboardInterrupt:
    print("\nSENDER: Engine Stopped.")
