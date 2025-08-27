#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Command to write WORD registers to flash memory.
"""

import sys
import click

from . import option_port, read_hex_words_from_stdin
from ...lib.protocol import FxProtocol, parse_int_or_hex


@click.command()
@option_port
@click.option("--address", required=True, help="Starting address to write to (decimal or hex with 0x prefix)")
@click.option("--dry-run", is_flag=True, help="Print request to console only, don't send it")
@click.option("--verbose", is_flag=True, help="Print detailed information about the communication")
def flash_write(
        port: str,
        address: str,
        dry_run: bool,
        verbose: bool,
):
    """Write WORD registers to flash memory."""
    try:
        # Parse address
        addr_int = parse_int_or_hex(address)
        value_list = read_hex_words_from_stdin()

        with FxProtocol(port, dry_run=dry_run, verbose=verbose) as protocol:
            if not protocol.start_communication():
                raise ValueError("Failed to establish communication with PLC")

            # do something
            protocol.send_command(b'F50100060')

            # BS 6025 => set M8037, "prohibit all outputs"=true
            protocol.send_command_expect_ack(b'E72560')

            # (may be set M8118 here)

            # do something with 805C address
            protocol.send_command_expect_ack(b'F71805C1FD5C0FF')

            # do something
            protocol.send_command(b'F50106960')

            protocol.write_flash(addr_int, value_list)

            # (may be clear M8118 here)

            protocol.lock_flash()

            # BC 6025 => clear M8037, "prohibit all outputs"=false
            protocol.send_command_expect_ack(b'E82560')

            # If not dry run, display confirmation
            if not dry_run and verbose:
                print(f"Flash memory written to address {address} (0x{addr_int:X}):", file=sys.stderr)
                for i, value in enumerate(value_list):
                    print(f"  [0x{addr_int + i:X}]: {value} (0x{value:04X})", file=sys.stderr)
    
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)
