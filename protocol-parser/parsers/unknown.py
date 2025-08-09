#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parser for unknown messages.
"""

from typing import Any, Optional
from ..constants import *


def parse_unknown(payload_ascii: str) -> dict[str, Any]:
    """
    Parse an unknown message.
    
    Args:
        payload_ascii: The ASCII payload to parse
        
    Returns:
        A dictionary with the parsed message
    """
    # For unknown commands, use U_XX format with first 2 chars of payload
    prefix = payload_ascii[:2] if len(payload_ascii) >= 2 else payload_ascii.ljust(2, '0')
    
    return {
        "what": f"U_{prefix}",
        "address": None,
        "size": None,
        "data": payload_ascii
    }


def parse_unknown_bytes(capdata_bytes: bytes) -> dict[str, Any]:
    """
    Parse an unknown message from bytes.
    
    Args:
        capdata_bytes: The bytes to parse
        
    Returns:
        A dictionary with the parsed message
    """
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