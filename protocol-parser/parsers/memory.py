#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parser for Memory (MR and MW) messages.
"""

from typing import Any
from .constants import *
from .common import extract_values_from_payload, extract_address_and_size


def parse_mr(payload_ascii: str) -> dict[str, Any]:
    """
    Parse a Memory read message.
    
    Args:
        payload_ascii: The ASCII payload to parse
        
    Returns:
        A dictionary with the parsed message
    """
    result = {
        "what": "MR",
        "address": None,
        "size": None,
        "data": payload_ascii
    }
    
    # Check for special payloads (TYP and VER)
    if payload_ascii == TYP_PAYLOAD:
        result["address"] = "0E02"
        result["size"] = "02"
        result["comment"] = "PLC Type"
        return result
    
    elif payload_ascii == VER_PAYLOAD:
        result["address"] = "0ECA"
        result["size"] = "02"
        result["comment"] = "PLC Version"
        return result
    
    # Check if this is a '0' command (PC_READ_byte)
    if len(payload_ascii) >= 1 and payload_ascii[0] == '0':
        if len(payload_ascii) >= 7:  # '0' + 4 chars for address + 2 chars for size
            # Extract address and size
            address_hex, _, size_int = extract_address_and_size(payload_ascii, 1)
            result["address"] = address_hex
            
            # Convert size to hex string
            result["size"] = f"{size_int:02X}"
            
            # For responses, extract values
            if len(payload_ascii) > 7:
                values = extract_values_from_payload(payload_ascii, 7)
                if values:
                    result["values"] = values
    
    return result


def parse_mw(payload_ascii: str) -> dict[str, Any]:
    """
    Parse a Memory write message.
    
    Args:
        payload_ascii: The ASCII payload to parse
        
    Returns:
        A dictionary with the parsed message
    """
    result = {
        "what": "MW",
        "address": None,
        "size": None,
        "data": payload_ascii
    }
    
    # Check if this is a '1' command (PC_WRITE_byte)
    if len(payload_ascii) >= 1 and payload_ascii[0] == '1':
        if len(payload_ascii) >= 7:  # '1' + 4 chars for address + 2 chars for size
            # Extract address and size
            address_hex, _, size_int = extract_address_and_size(payload_ascii, 1)
            result["address"] = address_hex
            
            # Size is already in bytes for write commands
            result["size"] = f"{size_int:02X}"
            
            # Extract values
            if len(payload_ascii) > 7:
                values = extract_values_from_payload(payload_ascii, 7)
                if values:
                    result["values"] = values
    
    return result