#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Common functions for the protocol parser.
"""

import binascii
from typing import Any, Optional
from .constants import *


def hex_to_bytes(hex_str: str) -> bytes:
    """Convert a hex string to bytes."""
    return binascii.unhexlify(hex_str)


def is_host(src: str) -> bool:
    """Check if the source is the host."""
    return src == "host"


def bytes_to_hex_space_separated(data: bytes) -> str:
    """Convert bytes to a space-separated hex string."""
    return ' '.join([f"{b:02X}" for b in data])


def parse_enq_ack(capdata_bytes: bytes) -> Optional[dict[str, Any]]:
    """Parse ENQ and ACK messages."""
    if len(capdata_bytes) == 1:
        if capdata_bytes[0] == ENQ:
            return {"what": ENQ_TYPE, "address": None, "size": None}
        elif capdata_bytes[0] == ACK:
            return {"what": ACK_TYPE, "address": None, "size": None}
    return None


def extract_values_from_payload(payload_ascii: str, start_index: int = 0) -> list[int]:
    """
    Extract values from a payload.
    
    Args:
        payload_ascii: The ASCII payload to extract values from
        start_index: The index to start extracting values from
        
    Returns:
        A list of extracted values
    """
    values = []
    for i in range(start_index, len(payload_ascii), 4):
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
    
    return values


def extract_address_and_size(payload_ascii: str, offset: int) -> tuple[str, str, int]:
    """
    Extracts the address and size from a payload.
    
    Args:
        payload_ascii: The ASCII payload to parse
        offset: The offset to start parsing from
        
    Returns:
        A tuple containing the address, size, and size in bytes
    """
    address_hex = payload_ascii[offset:offset+4]
    size_hex = payload_ascii[offset+4:offset+6]
    size_int = int(size_hex, 16)
    return address_hex, size_hex, size_int