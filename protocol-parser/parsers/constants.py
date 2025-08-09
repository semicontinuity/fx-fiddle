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
PR_PREFIX = "E00"  # Parameter read (formerly DR)
FR_PREFIX = "E01"  # Flash read (formerly MR)
PW_PREFIX = "E10"  # Parameter write (formerly DW)
FW_PREFIX = "E11"  # Flash write (formerly MW)
BS_PREFIX = "E7"   # Bit Set
BC_PREFIX = "E8"   # Bit Clear
MR_PREFIX = "0"    # Memory Read
MW_PREFIX = "1"    # Memory Write

# Special payloads
TYP_PAYLOAD = "00E0202"  # PLC type command
VER_PAYLOAD = "00ECA02"  # PLC version command

# Message types
ENQ_TYPE = "ENQ"
ACK_TYPE = "ACK"
PR_TYPE = "PR"  # Parameter read (formerly DR)
FR_TYPE = "FR"  # Flash read (formerly MR)
PW_TYPE = "PW"  # Parameter write (formerly DW)
FW_TYPE = "FW"  # Flash write (formerly MW)
BS_TYPE = "BS"
BC_TYPE = "BC"
TYP_TYPE = "TYP"
VER_TYPE = "VER"
MR_TYPE = "MR"  # Memory Read
MW_TYPE = "MW"  # Memory Write
UNK_TYPE = "UNK"  # Unknown