#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Command to disassemble FX3U PLC program from STDIN.
"""

import sys
import binascii
from typing import List

import click

from ..lib.disassembler import disassemble_program

def parse_input_to_words(input_data: str, is_hex: bool = False) -> List[int]:
    """
    Parse input data into a list of 16-bit words.
    
    Args:
        input_data: The input data as a string
        is_hex: If True, input is treated as space-separated hexadecimal 16-bit words
                If False, input is treated as binary data
    
    Returns:
        List of 16-bit words
    
    Raises:
        ValueError: If the input data is invalid
    """
    all_words = []
    
    if is_hex:
        # Parse input as space-separated hexadecimal 16-bit words
        hex_words = input_data.split()
        for hex_word in hex_words:
            try:
                word = int(hex_word, 16)
                all_words.append(word)
            except ValueError:
                raise ValueError(f"Invalid hexadecimal value '{hex_word}'")
    else:
        # Parse input as binary data
        # Each 16-bit word is represented by 2 bytes in little-endian format
        binary_data = input_data.encode('latin1') if isinstance(input_data, str) else input_data
        
        # Ensure we have an even number of bytes
        if len(binary_data) % 2 != 0:
            raise ValueError("Binary input must contain an even number of bytes")
        
        # Convert pairs of bytes to 16-bit words (little-endian)
        for i in range(0, len(binary_data), 2):
            word = binary_data[i] | (binary_data[i+1] << 8)
            all_words.append(word)
    
    return all_words


@click.command()
@click.option("--hex", is_flag=True, help="Input is in hexadecimal format (space-separated 16-bit words)")
def program_disassemble(
        hex: bool,
):
    """Disassemble FX3U PLC program from STDIN."""
    try:
        # Read input from STDIN
        input_data = sys.stdin.read().strip()
        
        # Parse input into 16-bit words
        all_words = parse_input_to_words(input_data, hex)
        
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
