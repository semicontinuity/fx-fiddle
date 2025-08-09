#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parser for Flash (FR and FW) messages.
"""

from typing import Any, List
from .constants import *
from .common import extract_values_from_payload


def parse_fr(payload_ascii: str) -> dict[str, Any]:
    """
    Parse a Flash read message.
    
    Args:
        payload_ascii: The ASCII payload to parse
        
    Returns:
        A dictionary with the parsed message
    """
    result = {
        "what": FR_TYPE,
        "address": None,
        "size": None,
        "data": payload_ascii
    }
    
    if len(payload_ascii) >= 9:
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
        if len(payload_ascii) > 9:
            values = extract_values_from_payload(payload_ascii, 9)
            if values:
                result["values"] = values
    
    return result


def parse_fw(payload_ascii: str) -> dict[str, Any]:
    """
    Parse a Flash write message.
    
    Args:
        payload_ascii: The ASCII payload to parse
        
    Returns:
        A dictionary with the parsed message
    """
    result = {
        "what": FW_TYPE,
        "address": None,
        "size": None,
        "data": payload_ascii
    }
    
    if len(payload_ascii) >= 9:
        # Extract address and size
        address_hex = payload_ascii[3:7]
        size_hex = payload_ascii[7:9]
        result["address"] = address_hex
        
        # Size is already in bytes for write commands
        size_int = int(size_hex, 16)
        result["size"] = f"{size_int:02X}"
        
        # Extract values
        values = extract_values_from_payload(payload_ascii, 9)
        if values:
            result["values"] = values
    
    return result