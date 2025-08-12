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
                values = protocol.read_flash(current_address, CHUNK_SIZE // 2)
                
                if not dry_run and values:
                    # Check for termination
                    while len(values) >= 1 and values[-1] == 0xFFFF:
                        should_continue = False
                        values = values[:-1]
                    
                    all_words.extend(values)
                
                current_address += CHUNK_SIZE
            
            # Disassemble the program
            disassembled = disassemble_program(all_words)
            
            # Print the disassembled program
            for instruction_words, disassembled_text in disassembled:
                # Format the instruction words
                words_hex = " ".join(f"{word:04X}" for word in instruction_words)
                print(f"{words_hex}\t{disassembled_text}")
                
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)
