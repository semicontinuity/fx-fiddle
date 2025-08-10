#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Command to read the program header from the PLC.
"""

import sys
import click

from . import option_port
from ...lib.protocol import FxProtocol


@click.command("read")
@option_port
@click.option("--dry-run", is_flag=True, help="Print request to console only, don't send it")
@click.option("--verbose", is_flag=True, help="Print detailed information about the communication")
def program_header_read(
        port: str,
        dry_run: bool,
        verbose: bool,
):
    """Read the program header from the PLC."""
    try:
        with FxProtocol(port, dry_run=dry_run, verbose=verbose) as protocol:
            # The program header is 92 bytes (46 words) long
            header_data = protocol.read_flash(0, 46)  # 92 bytes = 46 words
            
            if header_data:
                print_commented_header(header_data)
            else:
                raise ValueError("Failed to read program header")
    
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


def print_commented_header(data: list[int]):
    """Prints a commented version of the program header."""
    
    # PLC Model Code
    plc_model = (data[0] & 0xFF) | ((data[0] >> 8) & 0xFF)
    print(f"0000-0001: PLC Model Code: 0x{plc_model:04X}")
    
    # Program Title
    title_bytes = b"".join([(d & 0xFF).to_bytes(1, 'little') + ((d >> 8) & 0xFF).to_bytes(1, 'little') for d in data[1:17]])
    title = title_bytes.decode('ascii', errors='replace').strip('\x00')
    print(f"0002-0021: Program Title: {title}")
    
    # Program Capacity
    capacity = data[17]
    print(f"0022-0023: Program Capacity: {capacity} steps")
    
    # File System Information
    # This part is not fully documented, so we'll just print the raw data
    print("0024-002B: File System Information (raw):")
    for i, word in enumerate(data[18:22]):
        print(f"  {0x24 + i*2:04X}: 0x{word:04X}")
        
    # Password
    password = "Set" if any(d != 0xFFFF for d in data[22:32]) else "Not Set"
    print(f"002C-003F: Password: {password}")
    
    # Reserved / Options
    print("0040-005B: Reserved / Options:")
    print_options_area(data[32:])


def print_options_area(data: list[int]):
    """Prints a commented version of the options area."""
    
    # D8000: File Register Capacity
    print(f"  0040-0041: File Register Capacity (D8000): {data[0]}")
    
    # D8001: Latch Relay Range (Start)
    print(f"  0042-0043: Latch Relay Range Start (D8001): M{data[1]}")
    
    # D8002: Latch Relay Range (End)
    print(f"  0044-0045: Latch Relay Range End (D8002): M{data[2]}")
    
    # D8003: Latch State Relay Range
    print(f"  0046-0047: Latch State Relay Range (D8003): {data[3]}")
    
    # D8004: Latch Timer Range
    print(f"  0048-0049: Latch Timer Range (D8004): T{data[4]}")
    
    # D8005: Latch Counter Range
    print(f"  004A-004B: Latch Counter Range (D8005): C{data[5]}")
    
    # D8006: Latch Data Register Range (Start)
    print(f"  004C-004D: Latch Data Register Start (D8006): D{data[6]}")
    
    # D8007: Latch Data Register Range (End)
    print(f"  004E-004F: Latch Data Register End (D8007): D{data[7]}")
    
    # D8008: Special Memory Allocation
    print_special_memory_allocation(data[8])
    
    # Reserved for System
    print("  0052-005B: Reserved for System")


def print_special_memory_allocation(value: int):
    """Prints a commented version of the special memory allocation bitfield."""
    
    print(f"  0050-0051: Special Memory Allocation (D8008): 0x{value:04X}")
    
    flags = {
        0: "Enable Analog I/O",
        1: "Enable Positioning Mode",
        2: "Enable High-Speed Counter (HSC) Mode",
        3: "Enable CAM/Rotary Encoder Mode",
        4: "Enable Serial Port 1 (RS-232)",
        5: "Enable Serial Port 1 (RS-485)",
        6: "Enable CANopen Module",
        7: "Enable PID Auto-Tuning"
    }
    
    for bit, description in flags.items():
        if (value >> bit) & 1:
            print(f"    - {description}: ON")