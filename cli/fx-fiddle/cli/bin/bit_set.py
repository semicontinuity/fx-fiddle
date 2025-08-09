#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Command to set a bit at the specified address.
"""

import sys
import click

from . import option_port
from ...lib.protocol import FxProtocol, parse_int_or_hex


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
        
        # Create protocol handler and set the bit
        with FxProtocol(port, dry_run=dry_run, verbose=verbose) as protocol:
            success = protocol.set_bit(addr_int)
            
            if success:
                print(f"Bit set at address {address} (0x{addr_int:X})")
            else:
                raise ValueError("Failed to set bit")
    
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)