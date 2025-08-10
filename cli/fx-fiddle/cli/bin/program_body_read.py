#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Commands for program body operations.
"""

import sys

import click

from . import option_port
from ...lib.protocol import FxProtocol


@click.command()
@option_port
@click.option("--dry-run", is_flag=True, help="Print request to console only, don't send it")
@click.option("--verbose", is_flag=True, help="Print detailed information about the communication")
def read(
        port: str,
        dry_run: bool,
        verbose: bool,
):
    """Read program body from PLC memory."""
    try:
        PROGRAM_START_ADDRESS = 0x805C
        CHUNK_SIZE = 0x80
        
        with FxProtocol(port, dry_run=dry_run, verbose=verbose) as protocol:
            current_address = PROGRAM_START_ADDRESS
            should_continue = True
            
            while should_continue:
                # Read chunk of data
                values = protocol.read_flash(current_address, CHUNK_SIZE // 2)  # Convert bytes to words
                
                if not dry_run and values:
                    # Check for termination condition ('FFFF')
                    while len(values) >= 0:
                        if len(values) >= 1 and values[-1] == 0xFFFF:
                            should_continue = False
                            values = values[:-1]  # Remove termination markers
                        else:
                            break
                    
                    ascii_output = []
                    for value in values:
                        ascii_output.append('%02X' % value)

                    print('\n'.join(ascii_output))
                
                current_address += CHUNK_SIZE
                
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)