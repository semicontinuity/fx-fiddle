#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Flash memory operations for the FX3U PLC.
"""

import sys

import click

from . import option_port
from ...lib.protocol import FxProtocol


@click.command()
@option_port
@click.option("--dry-run", is_flag=True, help="Print request to console only, don't send it")
@click.option("--verbose", is_flag=True, help="Print detailed information about the communication")
def flash_lock(
        port: str,
        dry_run: bool,
        verbose: bool,
):
    """Lock flash memory after programming."""
    try:
        with FxProtocol(port, dry_run=dry_run, verbose=verbose) as protocol:
            # Send flash lock command (ASCII 'B') - using send_command_expect_ack since we expect just an ACK
            success = protocol.send_command_expect_ack(b'B')

            if not dry_run:
                if success:
                    print("Flash memory locked successfully")
                else:
                    print("Failed to lock flash memory")

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)
