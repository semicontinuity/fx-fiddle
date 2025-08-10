#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Commands for program body operations with comprehensive FX2N PLC instruction decoding.
"""

import sys
from typing import Tuple, List

import click

from . import option_port
from ...lib.protocol import FxProtocol

# FX2N instruction set mapping with detailed decoding
FX2N_INSTRUCTIONS = {
    # Basic instructions
    0x00: ("LD", ["X{0:02X}"]),
    0x01: ("AND", ["X{0:02X}"]), 
    0x02: ("OR", ["X{0:02X}"]),
    0x03: ("OUT", ["Y{0:02X}"]),
    0x04: ("SET", ["Y{0:02X}"]),
    0x05: ("RST", ["Y{0:02X}"]),
    0x06: ("PLS", ["Y{0:02X}"]), 
    0x07: ("PLF", ["Y{0:02X}"]),
    0x08: ("END", []),
    0x09: ("NOP", []),
    0x0A: ("INV", []),
    0x0B: ("MPS", []),
    0x0C: ("MRD", []),
    0x0D: ("MPP", []),
    0x0E: ("ANB", []),
    0x0F: ("ORB", []),
    
    # Timer/Counter instructions
    0x10: ("TMR", ["T{0:02X}", "K{1:X}"]),
    0x11: ("CNT", ["C{0:02X}", "K{1:X}"]),
    
    # Application instructions
    0x20: ("MOV", ["D{0:02X}"]),
    0x21: ("ADD", ["D{0:02X}"]),
    0x22: ("SUB", ["D{0:02X}"]),
    0x23: ("MUL", ["D{0:02X}"]),
    0x24: ("DIV", ["D{0:02X}"]),
    0x25: ("CMP", ["D{0:02X}"]),
    0x26: ("ZCP", ["D{0:02X}"]),
    
    # Special functions
    0x30: ("CJ", ["P{0:02X}"]),
    0x31: ("CALL", ["P{0:02X}"]),
    0x32: ("RET", []),
    0x33: ("EI", []),
    0x34: ("DI", []),
    0x35: ("FEND", []),
    0x36: ("SRET", []),
    0x37: ("IRET", []),
    0x38: ("FOR", ["D{0:02X}"]),
    0x39: ("NEXT", []),
}

# Extended instructions with special handling
EXTENDED_INSTRUCTIONS = {
    0xA8: ("LD", ["M{0:02X}"]),
    0xA9: ("LD", ["M{0:02X}"]),
    0xAA: ("LD", ["M{0:02X}"]),
    0xAB: ("LD", ["M{0:02X}"]),
    0xAC: ("LD", ["M{0:02X}"]),
    0xAD: ("LD", ["M{0:02X}"]),
    0xB0: ("LABEL", ["P{0:02X}"]),
}

def decode_fx2n_instruction(word: int) -> Tuple[str, List[str]]:
    """Decode FX2N PLC instruction with detailed argument handling."""
    opcode = (word >> 8) & 0xFF
    operand = word & 0xFF
    
    # Check extended instructions first
    if opcode in EXTENDED_INSTRUCTIONS:
        instr, args_fmt = EXTENDED_INSTRUCTIONS[opcode]
        return (instr, [fmt.format(operand) for fmt in args_fmt])
    
    # Handle basic instructions
    if opcode in FX2N_INSTRUCTIONS:
        instr, args_fmt = FX2N_INSTRUCTIONS[opcode]
        
        # Special case for inverted instructions
        if operand >= 0x80 and instr in ["LD", "AND", "OR"]:
            instr += "I"
            operand -= 0x80
        
        # Special handling for timer/counter values
        if instr in ["TMR", "CNT"]:
            timer_val = opcode & 0x0F
            return (instr, [fmt.format(operand, timer_val) for fmt in args_fmt])
            
        return (instr, [fmt.format(operand) for fmt in args_fmt])
    
    # Special multi-word instructions
    if word == 0x000F:
        return ("END", [])
    elif word == 0xF7FF:
        return ("RET", [])
    
    return (f"UNK_{opcode:02X}", [f"0x{operand:02X}"])


@click.command()
@option_port
@click.option("--dry-run", is_flag=True, help="Print request to console only, don't send it")
@click.option("--verbose", is_flag=True, help="Print detailed information about the communication")
@click.option("--decode", is_flag=True, help="Decode instructions in IL format with arguments")
def program_body_read(
        port: str,
        dry_run: bool,
        verbose: bool,
        decode: bool,
):
    """Read program body from PLC memory with optional instruction decoding."""
    try:
        PROGRAM_START_ADDRESS = 0x805C
        CHUNK_SIZE = 0x80
        
        with FxProtocol(port, dry_run=dry_run, verbose=verbose) as protocol:
            current_address = PROGRAM_START_ADDRESS
            should_continue = True
            
            while should_continue:
                values = protocol.read_flash(current_address, CHUNK_SIZE // 2)
                
                if not dry_run and values:
                    # Check for termination
                    while len(values) >= 1 and values[-1] == 0xFFFF:
                        should_continue = False
                        values = values[:-1]
                    
                    if decode:
                        # Detailed decoded output
                        for value in values:
                            hex_str = f"{value:04X}"
                            instr, args = decode_fx2n_instruction(value)
                            args_str = " ".join(args) if args else ""
                            print(f"{hex_str}\t{instr} {args_str}".strip())
                    else:
                        # Original hex output
                        for value in values:
                            print(f"{value:04X}")
                
                current_address += CHUNK_SIZE
                
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)
