#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Command to read WORD registers from flash memory.
"""

import sys
import click

from . import option_port
from ...lib.protocol import FxProtocol, parse_int_or_hex


@click.command()
@option_port
@click.option("--address", required=True, help="Starting address to read from (decimal or hex with 0x prefix)")
@click.option("--size", required=True, help="Number of words to read (decimal or hex with 0x prefix)")
@click.option("--dry-run", is_flag=True, help="Print request to console only, don't send it")
@click.option("--verbose", is_flag=True, help="Print detailed information about the communication")
def flash_read(
        port: str,
        address: str,
        size: str,
        dry_run: bool,
        verbose: bool,
):
    """Read WORD registers from flash memory."""
    try:
        # Parse address and size
        addr_int = parse_int_or_hex(address)
        size_int = parse_int_or_hex(size)
        
        with FxProtocol(port, dry_run=dry_run, verbose=verbose) as protocol:
            # Read flash memory
            values = protocol.read_flash(addr_int, size_int)
            
            # If not dry run, display results
            if not dry_run and values:
                print(f"Flash memory read from address {address} (0x{addr_int:X}), size {size} (0x{size_int:X}):", file=sys.stderr)
                for i, value in enumerate(values):
                    if verbose:
                        print(f"  [0x{addr_int + i:X}]: {value} (0x{value:04X})")
                    else:
                        print(f"{value:04X}")
    
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)