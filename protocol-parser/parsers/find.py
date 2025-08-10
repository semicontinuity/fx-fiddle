#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parser for FIND messages.
"""

from typing import Any
from .constants import *
from .common import *


def parse_find(payload_ascii: str) -> dict[str, Any]:
    """
    Parse a FIND message.
    
    Args:
        payload_ascii: The ASCII payload to parse
        
    Returns:
        A dictionary with the parsed message
    """
    result = {
        "what": FIND_TYPE,
        "address": None,
        "size": None,
        "data": payload_ascii
    }
    
    if len(payload_ascii) == 11:
        address_hex, data_hex = extract_address_and_uint16(payload_ascii, 3)
        result["address"] = address_hex
        result["comment"] = data_hex
    
    return result