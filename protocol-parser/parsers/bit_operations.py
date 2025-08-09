#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parser for Bit Operations (BS and BC) messages.
"""

from typing import Any, Optional
from ..constants import *


def parse_bs(payload_ascii: str) -> dict[str, Any]:
    """
    Parse a Bit Set message.
    
    Args:
        payload_ascii: The ASCII payload to parse
        
    Returns:
        A dictionary with the parsed message
    """
    result = {
        "what": BS_TYPE,
        "address": None,
        "size": None,
        "data": payload_ascii
    }
    
    # Extract word address (lo-endian)
    if len(payload_ascii) >= 5:
        # Get the address part (2 bytes after "E7")
        address_lo = payload_ascii[2:4]
        address_hi = payload_ascii[4:6] if len(payload_ascii) >= 6 else "00"
        # Combine in correct order (lo-endian)
        address_hex = address_hi + address_lo
        result["address"] = address_hex
    
    return result


def parse_bc(payload_ascii: str) -> dict[str, Any]:
    """
    Parse a Bit Clear message.
    
    Args:
        payload_ascii: The ASCII payload to parse
        
    Returns:
        A dictionary with the parsed message
    """
    result = {
        "what": BC_TYPE,
        "address": None,
        "size": None,
        "data": payload_ascii
    }
    
    # Extract word address (lo-endian)
    if len(payload_ascii) >= 5:
        # Get the address part (2 bytes after "E8")
        address_lo = payload_ascii[2:4]
        address_hi = payload_ascii[4:6] if len(payload_ascii) >= 6 else "00"
        # Combine in correct order (lo-endian)
        address_hex = address_hi + address_lo
        result["address"] = address_hex
    
    return result