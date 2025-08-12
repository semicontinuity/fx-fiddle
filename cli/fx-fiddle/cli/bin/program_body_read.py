#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Commands for program body operations with comprehensive FX3U PLC instruction decoding.
"""

import sys

import click

from . import option_port
from ..lib.disassembler import disassemble_program
from ...lib.protocol import FxProtocol


@click.command()
@option_port
@click.option("--dry-run", is_flag=True, help="Print request to console only, don't send it")
@click.option("--verbose", is_flag=True, help="Print detailed information about the communication")
def program_body_read(
        port: str,
        dry_run: bool,
        verbose: bool,
):
    """Read program body from PLC memory with instruction disassembly."""
    try:
        PROGRAM_START_ADDRESS = 0x805C
        CHUNK_SIZE = 0x80
        
        with FxProtocol(port, dry_run=dry_run, verbose=verbose) as protocol:
            current_address = PROGRAM_START_ADDRESS
            should_continue = True
            all_words = []
            
            while should_continue:
                if verbose:
                    print(f"Reading 0x{CHUNK_SIZE:04X} of flash at 0x{current_address:04X}")
                values = protocol.read_flash(current_address, CHUNK_SIZE)
                
                if not dry_run and values:
                    # Check for termination
                    while len(values) >= 1 and values[-1] == 0xFFFF:
                        should_continue = False
                        values = values[:-1]
                    
                    all_words.extend(values)
                
                current_address += CHUNK_SIZE
            
            # Disassemble the program
            disassembled = disassemble_program(all_words)
            
            # Print the disassembled program with instruction offsets
            offset = 0
            for instruction_words, disassembled_text in disassembled:
                # Format the instruction words
                words_hex = " ".join(f"{word:04X}" for word in instruction_words)
                # Format the instruction offset in hex (relative to program start)
                offset_hex = f"0x{offset:04X}"
                print(f"{offset_hex}:\t{words_hex}\t{disassembled_text}")
                offset += len(instruction_words) * 2  # Each word is 2 bytes
                
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)
