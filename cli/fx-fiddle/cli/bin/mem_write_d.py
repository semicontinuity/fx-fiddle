#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Command to write WORD registers to memory.
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
@click.option("--address", required=True, help="Starting address to write to (decimal or hex with 0x prefix)")
@click.option("--values", required=True, help="Comma-separated list of values to write (decimal or hex with 0x prefix)")
@click.option("--dry-run", is_flag=True, help="Print request to console only, don't send it")
@click.option("--verbose", is_flag=True, help="Print detailed information about the communication")
def mem_write_d(
        port: str,
        address: str,
        values: str,
        dry_run: bool,
        verbose: bool,
):
    """Write WORD registers to memory."""
    try:
        # Parse address
        addr_int = parse_int_or_hex(address)
        
        # Parse values
        value_list = []
        for val_str in values.split(','):
            val_str = val_str.strip()
            if val_str:
                value_list.append(parse_int_or_hex(val_str))
        
        if not value_list:
            click.echo("Error: No values provided", err=True)
            sys.exit(1)
        
        # Create protocol handler
        with FxProtocol(port, dry_run=dry_run, verbose=verbose) as protocol:
            # Write memory
            protocol.write_memory(addr_int, value_list)
            
            # If not dry run, display confirmation
            if not dry_run:
                print(f"Memory written to address {address} (0x{addr_int:X}):")
                for i, value in enumerate(value_list):
                    print(f"  [0x{addr_int + i:X}]: {value} (0x{value:04X})")
    
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)