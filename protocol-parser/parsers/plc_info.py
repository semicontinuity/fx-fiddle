#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parser for PLC Information (TYP and VER) messages.
"""

from typing import Any, Optional
from .constants import *


def parse_typ(payload_ascii: str) -> dict[str, Any]:
    """
    Parse a PLC Type message.
    
    Args:
        payload_ascii: The ASCII payload to parse
        
    Returns:
        A dictionary with the parsed message
    """
    return {
        "what": TYP_TYPE,
        "address": None,
        "size": None,
        "data": payload_ascii
    }


def parse_ver(payload_ascii: str) -> dict[str, Any]:
    """
    Parse a PLC Version message.
    
    Args:
        payload_ascii: The ASCII payload to parse
        
    Returns:
        A dictionary with the parsed message
    """
    return {
        "what": VER_TYPE,
        "address": None,
        "size": None,
        "data": payload_ascii
    }