import struct


dbc_db = {
    0x100: {
        "message_name": "Engine_Data",
        "signals": {
            "Engine_Speed": {
                "start_bit": 7,     
                "length": 16,       
                "factor": 0.5,      
                "offset": -20      
            },
        }
    }
}


def decode_can_message(can_id, raw_data_bytes, db):
    if can_id not in db:
        return f"Unknown ID: {hex(can_id)}"
    
    message_def = db[can_id]
    decoded_values = {}
    
  
    full_payload_int = int.from_bytes(raw_data_bytes, byteorder='little')
    
    print(f"Receiver: Decoding {message_def['message_name']} (ID: {hex(can_id)})...")
    

    for signal_name, specs in message_def['signals'].items():
        start = specs['start_bit']
        length = specs['length']
        factor = specs['factor']
        offset = specs['offset']
        
  
        mask = (1 << length) - 1
        

        raw_val = (full_payload_int >> start) & mask
        

        phys_val = (raw_val * factor) + offset
        
        decoded_values[signal_name] = phys_val
        
    return decoded_values


raw_payload = (6040 << 7).to_bytes(8, byteorder='little') 


result = decode_can_message(0x100, raw_payload, dbc_db)

print("-" * 30)
print("Final Output:", result)
print("-" * 30)
