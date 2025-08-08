#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Command to set a bit at the specified address.
"""

import sys
import click

from . import option_port
from ...lib.protocol import FxProtocol


def parse_int_or_hex(value: str) -> int:
    """Parse a string as decimal or hex (with 0x prefix)."""
    if value.lower().startswith('0x'):
        return int(value, 16)
    return int(value)


@click.command()
@option_port
@click.option("--address", required=True, help="Address of the bit to set (decimal or hex with 0x prefix)")
@click.option("--dry-run", is_flag=True, help="Print request to console only, don't send it")
@click.option("--verbose", is_flag=True, help="Print detailed information about the communication")
def bit_set(
        port: str,
        address: str,
        dry_run: bool,
        verbose: bool,
):
    """Set a bit at the specified address."""
    try:
        # Parse address
        addr_int = parse_int_or_hex(address)
        
        # Create protocol handler
        with FxProtocol(port, dry_run=dry_run, verbose=verbose) as protocol:
            # Start communication
            if not protocol.start_communication():
                raise ValueError("Failed to establish communication with PLC")
            
            # Create request payload
            # Format: 'E7' + (2 hex ASCII chars for low byte) + (2 hex ASCII chars for high byte)
            payload = bytearray(b'E7')
            
            # Add address in lo-endian format (low byte first, then high byte)
            low_byte = addr_int & 0xFF
            high_byte = (addr_int >> 8) & 0xFF
            
            # Convert to ASCII hex chars
            from ...lib.protocol import int_to_hex_chars
            low_byte_chars = int_to_hex_chars(low_byte, 2)
            high_byte_chars = int_to_hex_chars(high_byte, 2)
            
            # Add to payload
            payload.extend(low_byte_chars)
            payload.extend(high_byte_chars)
            
            # Send command and get response
            response = protocol.send_command(payload)
            
            # If not dry run, display results
            if not dry_run:
                print(f"Bit set at address {address} (0x{addr_int:X})")
    
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)