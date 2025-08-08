#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sys
import binascii
from collections import OrderedDict


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

def bytes_to_hex_space_separated(data):
    """Convert bytes to a space-separated hex string."""
    return ' '.join([f"{b:02X}" for b in data])

def parse_message(capdata_bytes, request_type=None, who=None):
    """Parse a message based on its content."""
    if len(capdata_bytes) == 1:
        # Single byte message
        if capdata_bytes[0] == ENQ:
            return {"what": "ENQ", "address": None, "size": None}
        elif capdata_bytes[0] == ACK:
            # Always set what='ACK' for ACK responses
            return {"what": "ACK", "address": None, "size": None}
        # For other single-byte messages, use U_XX format
        return {"what": f"U_{capdata_bytes[0]:02X}", "address": None, "size": None}
    
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
            
            # Convert payload to ASCII for parsing and data field
            payload_ascii = payload.decode('ascii', errors='replace')
            
            # Convert checksum to ASCII
            checksum_ascii = checksum.decode('ascii', errors='replace') if checksum else ""

            # Initialize result with default values
            result = {
                "what": "UNK",
                "address": None,
                "size": None,
                "sum": checksum_ascii,
                "data": payload_ascii
            }

            # If this is a PLC response to a request, use the same "what" value
            if who == "plc" and request_type in ["DR", "MR", "TYP", "VER"]:
                result["what"] = request_type
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
                            
                            # Convert size to integer and then to hex string
                            size_int = int(size_hex, 16)
                            # Size is in words, convert to bytes (2 bytes per word)
                            size_bytes = size_int * 2
                            result["size"] = f"{size_bytes:02X}"
                            
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
                            
                            # Convert size to integer and then to hex string
                            size_int = int(size_hex, 16)
                            # Size is in words, convert to bytes (2 bytes per word)
                            size_bytes = size_int * 2
                            result["size"] = f"{size_bytes:02X}"
                            
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
                            
                            # Size is already in bytes for write commands
                            size_int = int(size_hex, 16)
                            result["size"] = f"{size_int:02X}"
                            
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
                            
                            # Size is already in bytes for write commands
                            size_int = int(size_hex, 16)
                            result["size"] = f"{size_int:02X}"
                            
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
                    # Check for VER (PLC version) command
                    elif payload_ascii == "00ECA02":
                        result["what"] = "VER"
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
                        # For unknown commands, use U_XX format with first 2 chars of payload
                        prefix = payload_ascii[:2] if len(payload_ascii) >= 2 else payload_ascii.ljust(2, '0')
                        result["what"] = f"U_{prefix}"
                else:
                    # For unknown commands with short payload, use U_XX format with available chars
                    prefix = payload_ascii.ljust(2, '0')[:2]
                    result["what"] = f"U_{prefix}"

            return result
    
    # Unknown message type with no payload
    if len(capdata_bytes) > 1:
        # Try to get first two bytes after STX if present
        start_idx = 1 if capdata_bytes[0] == STX else 0
        if start_idx + 2 <= len(capdata_bytes):
            prefix = capdata_bytes[start_idx:start_idx+2].decode('ascii', errors='replace')
        else:
            prefix = capdata_bytes[start_idx:].decode('ascii', errors='replace').ljust(2, '0')
        return {"what": f"U_{prefix}", "address": None, "size": None}
    else:
        return {"what": "U_00", "address": None, "size": None}

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
                    # Parse the message
                    # Only pass request_type for STX/ETX messages, not for ACK
                    request_type = last_host_request if who == "plc" else None
                    parsed = parse_message(pending_bytes, request_type, who)
                    
                    # Create ordered result with 'who' before 'address'
                    result = OrderedDict()
                    result["who"] = who
                    result["what"] = parsed["what"]
                    result["address"] = parsed["address"]
                    result["size"] = parsed["size"]
                    
                    # Add other fields from parsed
                    for key, value in parsed.items():
                        if key not in ["what", "address", "size"]:
                            result[key] = value
                    
                    # Add capdata as space-separated hex
                    result["capdata"] = bytes_to_hex_space_separated(pending_bytes)
                    
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
                # Check if this is an ACK response
                is_ack = len(capdata_bytes) == 1 and capdata_bytes[0] == ACK
                
                # Parse the message
                # Only pass request_type for STX/ETX messages, not for ACK
                request_type = last_host_request if who == "plc" and not is_ack else None
                parsed = parse_message(capdata_bytes, request_type, who)
                
                # Create ordered result with 'who' before 'address'
                result = OrderedDict()
                result["who"] = who
                result["what"] = parsed["what"]
                result["address"] = parsed["address"]
                result["size"] = parsed["size"]
                
                # Add other fields from parsed
                for key, value in parsed.items():
                    if key not in ["what", "address", "size"]:
                        result[key] = value
                
                # Add capdata as space-separated hex
                result["capdata"] = bytes_to_hex_space_separated(capdata_bytes)
                
                # Update last_host_request if this is a host request
                if who == "host" and parsed["what"] in ["DR", "MR", "TYP", "VER", "BS", "BC"]:
                    last_host_request = parsed["what"]
                
                # Output as JSON line
                print(json.dumps(result))

if __name__ == "__main__":
    main()