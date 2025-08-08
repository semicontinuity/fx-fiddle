#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sys
import binascii


# Protocol constants
ENQ = 0x05  # Enquiry
ACK = 0x06  # Acknowledge
STX = 0x02  # Start of Text
ETX = 0x03  # End of Text

def hex_to_bytes(hex_str):
    """Convert a hex string to bytes."""
    return binascii.unhexlify(hex_str)

def is_host(src):
    """Check if the source is the host."""
    return src == "host"

def parse_message(capdata_bytes, request_type=None, who=None):
    """Parse a message based on its content."""
    if len(capdata_bytes) == 1:
        # Single byte message
        if capdata_bytes[0] == ENQ:
            return {"what": "ENQ", "address": None}
        elif capdata_bytes[0] == ACK:
            # If this is a response to BS or BC, keep the request type
            if who == "plc" and request_type in ["BS", "BC"]:
                return {"what": request_type, "address": None}
            else:
                return {"what": "ACK", "address": None}
        return {"what": "UNK", "address": None}
    
    # Check for STX/ETX message
    if len(capdata_bytes) >= 3 and capdata_bytes[0] == STX:
        etx_pos = -1
        for i in range(1, len(capdata_bytes)):
            if capdata_bytes[i] == ETX:
                etx_pos = i
                break
        
        if etx_pos != -1:
            # Extract payload and checksum
            payload = capdata_bytes[1:etx_pos]
            checksum = capdata_bytes[etx_pos+1:etx_pos+3] if etx_pos + 3 <= len(capdata_bytes) else b''
            
            # Convert payload to ASCII
            payload_ascii = payload.decode('ascii', errors='replace')
            
            # Convert checksum to ASCII
            checksum_ascii = checksum.decode('ascii', errors='replace') if checksum else ""

            result = {}

            # If this is a PLC response to a request, use the same "what" value
            if who == "plc" and request_type in ["DR", "MR", "TYP", "VER"]:
                result["what"] = request_type
                result["address"] = None  # Will be updated if address is found in payload
            else:
                # Determine message type based on payload
                if len(payload) >= 3:
                    if payload_ascii.startswith("E00"):
                        # Data Register read
                        result["what"] = "DR"
                        if len(payload) >= 9:
                            # Extract address and size
                            address_hex = payload_ascii[3:7]
                            size_hex = payload_ascii[7:9]
                            result["address"] = address_hex
                            result["size"] = int(size_hex, 16)
                            
                            # For responses, extract values
                            if len(payload) > 9:
                                values = []
                                for i in range(9, len(payload_ascii), 4):
                                    if i + 4 <= len(payload_ascii):
                                        # Extract high and low bytes (each 2 ASCII chars)
                                        high_byte_str = payload_ascii[i:i+2]
                                        low_byte_str = payload_ascii[i+2:i+4]
                                        
                                        # Swap high and low bytes (low-endian)
                                        word_str = low_byte_str + high_byte_str
                                        
                                        # Convert to integer
                                        try:
                                            word_value = int(word_str, 16)
                                            values.append(word_value)
                                        except ValueError:
                                            pass
                                
                                if values:
                                    result["values"] = values
                    
                    elif payload_ascii.startswith("E01"):
                        # Memory Register read
                        result["what"] = "MR"
                        if len(payload) >= 9:
                            # Extract address and size
                            address_hex = payload_ascii[3:7]
                            size_hex = payload_ascii[7:9]
                            result["address"] = address_hex
                            result["size"] = int(size_hex, 16)
                            
                            # For responses, extract values
                            if len(payload) > 9:
                                values = []
                                for i in range(9, len(payload_ascii), 4):
                                    if i + 4 <= len(payload_ascii):
                                        # Extract high and low bytes (each 2 ASCII chars)
                                        high_byte_str = payload_ascii[i:i+2]
                                        low_byte_str = payload_ascii[i+2:i+4]
                                        
                                        # Swap high and low bytes (low-endian)
                                        word_str = low_byte_str + high_byte_str
                                        
                                        # Convert to integer
                                        try:
                                            word_value = int(word_str, 16)
                                            values.append(word_value)
                                        except ValueError:
                                            pass
                                
                                if values:
                                    result["values"] = values
                        
                    elif payload_ascii.startswith("E10"):
                        # Data Register write
                        result["what"] = "DW"
                        if len(payload) >= 9:
                            # Extract address and size
                            address_hex = payload_ascii[3:7]
                            size_hex = payload_ascii[7:9]
                            result["address"] = address_hex
                            result["size"] = int(size_hex, 16)
                            
                            # Extract values
                            values = []
                            for i in range(9, len(payload_ascii), 4):
                                if i + 4 <= len(payload_ascii):
                                    # Extract high and low bytes (each 2 ASCII chars)
                                    high_byte_str = payload_ascii[i:i+2]
                                    low_byte_str = payload_ascii[i+2:i+4]
                                    
                                    # Swap high and low bytes (low-endian)
                                    word_str = low_byte_str + high_byte_str
                                    
                                    # Convert to integer
                                    try:
                                        word_value = int(word_str, 16)
                                        values.append(word_value)
                                    except ValueError:
                                        pass
                            
                            if values:
                                result["values"] = values
                    
                    elif payload_ascii.startswith("E11"):
                        # Memory Register write
                        result["what"] = "MW"
                        if len(payload) >= 9:
                            # Extract address and size
                            address_hex = payload_ascii[3:7]
                            size_hex = payload_ascii[7:9]
                            result["address"] = address_hex
                            result["size"] = int(size_hex, 16)
                            
                            # Extract values
                            values = []
                            for i in range(9, len(payload_ascii), 4):
                                if i + 4 <= len(payload_ascii):
                                    # Extract high and low bytes (each 2 ASCII chars)
                                    high_byte_str = payload_ascii[i:i+2]
                                    low_byte_str = payload_ascii[i+2:i+4]
                                    
                                    # Swap high and low bytes (low-endian)
                                    word_str = low_byte_str + high_byte_str
                                    
                                    # Convert to integer
                                    try:
                                        word_value = int(word_str, 16)
                                        values.append(word_value)
                                    except ValueError:
                                        pass
                            
                            if values:
                                result["values"] = values
                    # Check for TYP (PLC type) command
                    elif payload_ascii == "00E0202":
                        result["what"] = "TYP"
                        result["address"] = None
                    # Check for VER (PLC version) command
                    elif payload_ascii == "00ECA02":
                        result["what"] = "VER"
                        result["address"] = None
                    # Check for BS (Bit Set) command
                    elif payload_ascii.startswith("E7") and len(payload_ascii) >= 5:
                        result["what"] = "BS"
                        # Extract word address (lo-endian)
                        if len(payload_ascii) >= 5:
                            # Get the address part (2 bytes after "E7")
                            address_lo = payload_ascii[2:4]
                            address_hi = payload_ascii[4:6] if len(payload_ascii) >= 6 else "00"
                            # Combine in correct order (lo-endian)
                            address_hex = address_hi + address_lo
                            result["address"] = address_hex
                    # Check for BC (Bit Clear) command
                    elif payload_ascii.startswith("E8") and len(payload_ascii) >= 5:
                        result["what"] = "BC"
                        # Extract word address (lo-endian)
                        if len(payload_ascii) >= 5:
                            # Get the address part (2 bytes after "E8")
                            address_lo = payload_ascii[2:4]
                            address_hi = payload_ascii[4:6] if len(payload_ascii) >= 6 else "00"
                            # Combine in correct order (lo-endian)
                            address_hex = address_hi + address_lo
                            result["address"] = address_hex
                    else:
                        result["what"] = "UNK"
                        result["address"] = None
                else:
                    result["what"] = "UNK"
                    result["address"] = None

            result.update({
                "sum": checksum_ascii,
                "data": payload_ascii,
            })

            return result
    
    # Unknown message type
    return {"what": "UNK", "address": None}

def main():
    if len(sys.argv) != 2:
        print("Usage: python parse.py <input_json_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    try:
        with open(input_file, 'r') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error loading JSON file: {e}")
        sys.exit(1)
    
    # Process records
    pending_frames = {}  # Store incomplete frames by source
    last_host_request = None  # Track the last request type from host
    
    for record in data:
        if "layers" not in record["_source"]:
            continue
        
        layers = record["_source"]["layers"]
        
        # Skip records without usb.capdata
        if "usb.capdata" not in layers:
            continue
        
        # Get source and determine who is sending
        src = layers.get("usb.src", [""])[0]
        who = "host" if is_host(src) else "plc"
        
        # Get capdata
        capdata_hex = layers["usb.capdata"][0]
        capdata_bytes = hex_to_bytes(capdata_hex)
        
        # Check if this is a continuation of a previous frame
        if who in pending_frames:
            # We have a pending frame, check if this completes it
            pending_bytes = pending_frames[who]["bytes"]
            
            # Append the new bytes (using bytearray)
            new_pending = bytearray(pending_bytes)
            new_pending.extend(capdata_bytes)
            pending_bytes = bytes(new_pending)
            
            # Check if we have a complete frame (has STX and ETX)
            if STX in pending_bytes and ETX in pending_bytes:
                # We have a complete frame
                etx_index = pending_bytes.index(ETX)
                if etx_index + 3 <= len(pending_bytes):  # ETX + 2 checksum bytes
                    # Process the complete frame
                    result = {
                        "who": who,
                    }
                    
                    # Parse the message
                    request_type = last_host_request if who == "plc" else None
                    parsed = parse_message(pending_bytes, request_type, who)
                    result.update(parsed)
                    result.update({
                        "capdata": binascii.hexlify(pending_bytes).decode('ascii')
                    })
                    
                    # Update last_host_request if this is a host request
                    if who == "host" and parsed["what"] in ["DR", "MR", "TYP", "VER", "BS", "BC"]:
                        last_host_request = parsed["what"]

                    # Output as JSON line
                    print(json.dumps(result))
                    
                    # Clear pending frame
                    del pending_frames[who]
                else:
                    # Still waiting for more bytes (checksum)
                    pending_frames[who]["bytes"] = pending_bytes
            else:
                # Still waiting for more bytes
                pending_frames[who]["bytes"] = pending_bytes
        else:
            # New frame
            if STX in capdata_bytes and ETX not in capdata_bytes:
                # This is the start of a multi-frame message
                pending_frames[who] = {
                    "bytes": capdata_bytes
                }
            else:
                # This is a complete frame or a single-byte message
                result = {
                    "who": who,
                }
                
                # Parse the message
                request_type = last_host_request if who == "plc" else None
                parsed = parse_message(capdata_bytes, request_type, who)
                result.update(parsed)
                result.update({
                    "capdata": capdata_hex
                })
                
                # Update last_host_request if this is a host request
                if who == "host" and parsed["what"] in ["DR", "MR", "TYP", "VER", "BS", "BC"]:
                    last_host_request = parsed["what"]

                # Output as JSON line
                print(json.dumps(result))

if __name__ == "__main__":
    main()