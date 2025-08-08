#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Command to clear a bit at the specified address.
"""

import sys
import click

from . import option_port
from ...lib.protocol import FxProtocol, ACK


def parse_int_or_hex(value: str) -> int:
    """Parse a string as decimal or hex (with 0x prefix)."""
    if value.lower().startswith('0x'):
        return int(value, 16)
    return int(value)


@click.command()
@option_port
@click.option("--address", required=True, help="Address of the bit to clear (decimal or hex with 0x prefix)")
@click.option("--dry-run", is_flag=True, help="Print request to console only, don't send it")
@click.option("--verbose", is_flag=True, help="Print detailed information about the communication")
def bit_clear(
        port: str,
        address: str,
        dry_run: bool,
        verbose: bool,
):
    """Clear a bit at the specified address."""
    try:
        # Parse address
        addr_int = parse_int_or_hex(address)
        
        # Create protocol handler
        with FxProtocol(port, dry_run=dry_run, verbose=verbose) as protocol:
            # Start communication
            if not protocol.start_communication():
                raise ValueError("Failed to establish communication with PLC")
            
            # Create request payload
            # Format: 'E8' + (2 hex ASCII chars for low byte) + (2 hex ASCII chars for high byte)
            payload = bytearray(b'E8')
            
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
            
            # Create the full request with STX, ETX, and checksum
            from ...lib.protocol import STX, ETX, calculate_checksum
            request = bytearray([STX])
            request.extend(payload)
            
            # Calculate checksum including ETX
            checksum_data = bytearray(payload)
            checksum_data.append(ETX)
            checksum = calculate_checksum(checksum_data)
            
            # Complete the request with ETX and checksum
            request.append(ETX)
            request.extend(checksum)
            
            # If dry run, just print the request and return
            if dry_run:
                print("Dry run mode - Request that would be sent:")
                print(f"STX: 0x{STX:02X}")
                print(f"Payload (hex): {' '.join([f'0x{b:02X}' for b in payload])}")
                print(f"Payload (ASCII): {payload.decode('ascii', errors='replace')}")
                print(f"ETX: 0x{ETX:02X}")
                print(f"Checksum: {' '.join([f'0x{b:02X}' for b in checksum])} (ASCII: {checksum.decode('ascii', errors='replace')})")
                print(f"Complete request: {' '.join([f'0x{b:02X}' for b in request])}")
                return
            
            # Print verbose information if requested
            if verbose:
                print("Sending request:")
                print(f"STX: 0x{STX:02X}")
                print(f"Payload (hex): {' '.join([f'0x{b:02X}' for b in payload])}")
                print(f"Payload (ASCII): {payload.decode('ascii', errors='replace')}")
                print(f"ETX: 0x{ETX:02X}")
                print(f"Checksum: {' '.join([f'0x{b:02X}' for b in checksum])} (ASCII: {checksum.decode('ascii', errors='replace')})")
                print(f"Complete request: {' '.join([f'0x{b:02X}' for b in request])}")
            
            # Send request
            if protocol.port is None:
                raise ValueError("Serial port is not open")
            protocol.port.write(request)
            
            # Read response (expecting ACK)
            response = protocol.port.read(1)
            
            # Check if response is ACK
            if response and response[0] == ACK:
                if verbose:
                    print("Received ACK:")
                    print(f"Hex bytes: 0x{ACK:02X}")
                print(f"Bit cleared at address {address} (0x{addr_int:X})")
            else:
                if response:
                    print(f"Did not receive ACK, got: 0x{response[0]:02X}")
                else:
                    print("No response received")
                raise ValueError("Failed to clear bit")
    
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)