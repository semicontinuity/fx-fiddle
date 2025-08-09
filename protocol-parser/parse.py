#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main parser for the protocol.
"""

import json
import sys
import binascii
from typing import Any, Optional, List, Tuple
from collections import OrderedDict

from parsers.constants import *
from parsers.common import hex_to_bytes, is_host, bytes_to_hex_space_separated, parse_enq_ack
from parsers.param import parse_pr, parse_pw
from parsers.flash import parse_fr, parse_fw
from parsers.bit_operations import parse_bs, parse_bc
from parsers.memory import parse_mr, parse_mw
from parsers.unknown import parse_unknown, parse_unknown_bytes


def parse_message(capdata_bytes: bytes, request_type: Optional[str] = None, who: Optional[str] = None) -> dict[str, Any]:
    """Parse a message based on its content."""
    # Check for single byte message (ENQ or ACK)
    if len(capdata_bytes) == 1:
        result = parse_enq_ack(capdata_bytes)
        if result:
            return result
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
                "what": UNK_TYPE,
                "address": None,
                "size": None,
                "comment": None,
                "data": payload_ascii,
                "sum": checksum_ascii,
            }

            # If this is a PLC response to a request, use the same "what" value
            if who == "plc" and request_type in [PR_TYPE, FR_TYPE, BS_TYPE, BC_TYPE, MR_TYPE, MW_TYPE]:
                result["what"] = request_type
                return result
            
            # Check for specific message types based on prefixes
            if payload_ascii.startswith(PR_PREFIX):
                return {**result, **parse_pr(payload_ascii)}
            
            elif payload_ascii.startswith(PW_PREFIX):
                return {**result, **parse_pw(payload_ascii)}
            
            elif payload_ascii.startswith(FR_PREFIX):
                return {**result, **parse_fr(payload_ascii)}
            
            elif payload_ascii.startswith(FW_PREFIX):
                return {**result, **parse_fw(payload_ascii)}
            
            elif payload_ascii.startswith(BS_PREFIX):
                return {**result, **parse_bs(payload_ascii)}
            
            elif payload_ascii.startswith(BC_PREFIX):
                return {**result, **parse_bc(payload_ascii)}
            
            elif payload_ascii.startswith(MR_PREFIX):
                return {**result, **parse_mr(payload_ascii)}
            
            elif payload_ascii.startswith(MW_PREFIX):
                return {**result, **parse_mw(payload_ascii)}
            
            # Unknown message
            return {**result, **parse_unknown(payload_ascii)}
    
    # Unknown message type with no payload
    return parse_unknown_bytes(capdata_bytes)


def main() -> None:
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
    pending_frames: dict[str, dict[str, bytes]] = {}  # Store incomplete frames by source
    last_host_request: Optional[str] = None  # Track the last request type from host
    
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
                    if who == "host" and parsed["what"] in [PR_TYPE, FR_TYPE, BS_TYPE, BC_TYPE, MR_TYPE, MW_TYPE]:
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
                if who == "host" and parsed["what"] in [PR_TYPE, FR_TYPE, BS_TYPE, BC_TYPE, MR_TYPE, MW_TYPE]:
                    last_host_request = parsed["what"]
                
                # Output as JSON line
                print(json.dumps(result))


if __name__ == "__main__":
    main()