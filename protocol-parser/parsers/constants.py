#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Constants for the protocol parser.
"""

# Protocol constants
ENQ = 0x05  # Enquiry
ACK = 0x06  # Acknowledge
STX = 0x02  # Start of Text
ETX = 0x03  # End of Text

# Message prefixes
DR_PREFIX = "E00"  # Data Register read
MR_PREFIX = "E01"  # Memory Register read
DW_PREFIX = "E10"  # Data Register write
MW_PREFIX = "E11"  # Memory Register write
BS_PREFIX = "E7"   # Bit Set
BC_PREFIX = "E8"   # Bit Clear

# Special payloads
TYP_PAYLOAD = "00E0202"  # PLC type command
VER_PAYLOAD = "00ECA02"  # PLC version command

# Message types
ENQ_TYPE = "ENQ"
ACK_TYPE = "ACK"
DR_TYPE = "DR"
MR_TYPE = "MR"
DW_TYPE = "DW"
MW_TYPE = "MW"
BS_TYPE = "BS"
BC_TYPE = "BC"
TYP_TYPE = "TYP"
VER_TYPE = "VER"
UNK_TYPE = "UNK"  # Unknown