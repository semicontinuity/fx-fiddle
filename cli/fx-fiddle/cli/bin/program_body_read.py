#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Commands for program body operations with comprehensive FX2N PLC instruction decoding.
"""

import sys
from typing import Tuple, List, Dict, Optional, Any

import click

from . import option_port
from ...lib.protocol import FxProtocol

# Basic bit instruction opcodes (high byte)
# Format: [I]O where [I] is instruction class and O is operand/memory area
BASIC_BIT_INSTRUCTIONS = {
    # LD instructions (I=2)
    0x20: ("LD", "S", "Step Relay Bank 0"),
    0x21: ("LD", "S", "Step Relay Bank 1"),
    0x22: ("LD", "S", "Step Relay Bank 2"),
    0x23: ("LD", "S", "Step Relay Bank 3"),
    0x24: ("LD", "T", "Timer (Coil)"),
    0x25: ("LD", "Y", "Output"),
    0x26: ("LD", "T", "Timer (Contact)"),
    0x28: ("LD", "X", "Input Bank 0"),
    0x29: ("LD", "X", "Input Bank 1"),
    0x2A: ("LD", "X", "Input Bank 2"),
    0x2B: ("LD", "X", "Input Bank 3"),
    0x2C: ("LD", "X", "Input Bank 4"),
    0x2D: ("LD", "X", "Input Bank 5"),
    0x2E: ("LD", "C", "Counter (Contact)"),
    0x2F: ("LD", "M", "Special Relay"),
    
    # LDI instructions (I=3)
    0x30: ("LDI", "S", "Step Relay Bank 0"),
    0x31: ("LDI", "S", "Step Relay Bank 1"),
    0x32: ("LDI", "S", "Step Relay Bank 2"),
    0x33: ("LDI", "S", "Step Relay Bank 3"),
    0x34: ("LDI", "T", "Timer (Coil)"),
    0x35: ("LDI", "Y", "Output"),
    0x36: ("LDI", "T", "Timer (Contact)"),
    0x38: ("LDI", "X", "Input Bank 0"),
    0x39: ("LDI", "X", "Input Bank 1"),
    0x3A: ("LDI", "X", "Input Bank 2"),
    0x3B: ("LDI", "X", "Input Bank 3"),
    0x3C: ("LDI", "X", "Input Bank 4"),
    0x3D: ("LDI", "X", "Input Bank 5"),
    0x3E: ("LDI", "C", "Counter (Contact)"),
    0x3F: ("LDI", "M", "Special Relay"),
    
    # AND instructions (I=4)
    0x40: ("AND", "S", "Step Relay Bank 0"),
    0x41: ("AND", "S", "Step Relay Bank 1"),
    0x42: ("AND", "S", "Step Relay Bank 2"),
    0x43: ("AND", "S", "Step Relay Bank 3"),
    0x44: ("AND", "T", "Timer (Coil)"),
    0x45: ("AND", "Y", "Output"),
    0x46: ("AND", "T", "Timer (Contact)"),
    0x48: ("AND", "X", "Input Bank 0"),
    0x49: ("AND", "X", "Input Bank 1"),
    0x4A: ("AND", "X", "Input Bank 2"),
    0x4B: ("AND", "X", "Input Bank 3"),
    0x4C: ("AND", "X", "Input Bank 4"),
    0x4D: ("AND", "X", "Input Bank 5"),
    0x4E: ("AND", "C", "Counter (Contact)"),
    0x4F: ("AND", "M", "Special Relay"),
    
    # ANI instructions (I=5)
    0x50: ("ANI", "S", "Step Relay Bank 0"),
    0x51: ("ANI", "S", "Step Relay Bank 1"),
    0x52: ("ANI", "S", "Step Relay Bank 2"),
    0x53: ("ANI", "S", "Step Relay Bank 3"),
    0x54: ("ANI", "T", "Timer (Coil)"),
    0x55: ("ANI", "Y", "Output"),
    0x56: ("ANI", "T", "Timer (Contact)"),
    0x58: ("ANI", "X", "Input Bank 0"),
    0x59: ("ANI", "X", "Input Bank 1"),
    0x5A: ("ANI", "X", "Input Bank 2"),
    0x5B: ("ANI", "X", "Input Bank 3"),
    0x5C: ("ANI", "X", "Input Bank 4"),
    0x5D: ("ANI", "X", "Input Bank 5"),
    0x5E: ("ANI", "C", "Counter (Contact)"),
    0x5F: ("ANI", "M", "Special Relay"),
    
    # OR instructions (I=6)
    0x60: ("OR", "S", "Step Relay Bank 0"),
    0x61: ("OR", "S", "Step Relay Bank 1"),
    0x62: ("OR", "S", "Step Relay Bank 2"),
    0x63: ("OR", "S", "Step Relay Bank 3"),
    0x64: ("OR", "T", "Timer (Coil)"),
    0x65: ("OR", "Y", "Output"),
    0x66: ("OR", "T", "Timer (Contact)"),
    0x68: ("OR", "X", "Input Bank 0"),
    0x69: ("OR", "X", "Input Bank 1"),
    0x6A: ("OR", "X", "Input Bank 2"),
    0x6B: ("OR", "X", "Input Bank 3"),
    0x6C: ("OR", "X", "Input Bank 4"),
    0x6D: ("OR", "X", "Input Bank 5"),
    0x6E: ("OR", "C", "Counter (Contact)"),
    0x6F: ("OR", "M", "Special Relay"),
    
    # ORI instructions (I=7)
    0x70: ("ORI", "S", "Step Relay Bank 0"),
    0x71: ("ORI", "S", "Step Relay Bank 1"),
    0x72: ("ORI", "S", "Step Relay Bank 2"),
    0x73: ("ORI", "S", "Step Relay Bank 3"),
    0x74: ("ORI", "T", "Timer (Coil)"),
    0x75: ("ORI", "Y", "Output"),
    0x76: ("ORI", "T", "Timer (Contact)"),
    0x78: ("ORI", "X", "Input Bank 0"),
    0x79: ("ORI", "X", "Input Bank 1"),
    0x7A: ("ORI", "X", "Input Bank 2"),
    0x7B: ("ORI", "X", "Input Bank 3"),
    0x7C: ("ORI", "X", "Input Bank 4"),
    0x7D: ("ORI", "X", "Input Bank 5"),
    0x7E: ("ORI", "C", "Counter (Contact)"),
    0x7F: ("ORI", "M", "Special Relay"),
    
    # OUT instructions (I=C)
    0xC0: ("OUT", "S", "Step Relay Bank 0"),
    0xC1: ("OUT", "S", "Step Relay Bank 1"),
    0xC2: ("OUT", "S", "Step Relay Bank 2"),
    0xC3: ("OUT", "S", "Step Relay Bank 3"),
    0xC4: ("OUT", "T", "Timer (Coil)"),
    0xC5: ("OUT", "Y", "Output"),
    0xC6: ("OUT", "T", "Timer (Contact)"),
    0xCE: ("OUT", "C", "Counter (Contact)"),
    0xCF: ("OUT", "M", "Special Relay"),
    
    # SET instructions (I=D)
    0xD0: ("SET", "S", "Step Relay Bank 0"),
    0xD1: ("SET", "S", "Step Relay Bank 1"),
    0xD2: ("SET", "S", "Step Relay Bank 2"),
    0xD3: ("SET", "S", "Step Relay Bank 3"),
    0xD5: ("SET", "Y", "Output"),
    0xDF: ("SET", "M", "Special Relay"),
    
    # RST instructions (I=E)
    0xE0: ("RST", "S", "Step Relay Bank 0"),
    0xE1: ("RST", "S", "Step Relay Bank 1"),
    0xE2: ("RST", "S", "Step Relay Bank 2"),
    0xE3: ("RST", "S", "Step Relay Bank 3"),
    0xE5: ("RST", "Y", "Output"),
    0xEF: ("RST", "M", "Special Relay"),
}

# Stack and Logic Block Instructions
STACK_LOGIC_INSTRUCTIONS = {
    0xFFFA: ("MPS", [], "Multi-Point Start"),
    0xFFFB: ("MRD", [], "Multi-Point Read"),
    0xFFFC: ("MPP", [], "Multi-Point Pop"),
    0xFFF9: ("ORB", [], "OR Block"),
    0xFFF8: ("ANB", [], "AND Block"),
    0xFFFD: ("INV", [], "Invert"),
}

# Special single-word instructions
SPECIAL_INSTRUCTIONS = {
    0x000F: ("END", [], "End of program"),
    0xF7FF: ("RET", [], "Return from subroutine"),
}

# Extended bit instructions (first word)
EXTENDED_BIT_INSTRUCTIONS = {
    0x01C2: ("LD", "Extended"),
    0x01C3: ("LDI", "Extended"),
    0x01C4: ("AND", "Extended"),
    0x01C5: ("ANI", "Extended"),
    0x01C6: ("OR", "Extended"),
    0x01C7: ("ORI", "Extended"),
    0x0002: ("OUT", "Extended M"),
    0x0003: ("SET", "Extended M"),
    0x0004: ("RST", "Extended M"),
    0x0005: ("OUT", "Extended S"),
    0x0006: ("SET", "Extended S"),
    0x0007: ("RST", "Extended S"),
}

# Pulsed (Edge) instructions (first word)
PULSED_INSTRUCTIONS = {
    0x01CA: ("LDP", "Rising Edge"),
    0x01CB: ("LDF", "Falling Edge"),
    0x01CC: ("ANDP", "Rising Edge"),
    0x01CD: ("ANDF", "Falling Edge"),
    0x01CE: ("ORP", "Rising Edge"),
    0x01CF: ("ORF", "Falling Edge"),
}

# Compare instructions (first word)
COMPARE_INSTRUCTIONS = {
    0x01D0: ("LD=", "Equal"),
    0x01D2: ("LD>", "Greater Than"),
    0x01D4: ("LD<", "Less Than"),
    0x01DA: ("LD<=", "Less Than or Equal"),
    0x01DC: ("LD>=", "Greater Than or Equal"),
    0x01E0: ("AND=", "Equal"),
    0x01E2: ("AND>", "Greater Than"),
    0x01E4: ("AND<", "Less Than"),
    0x01EA: ("AND<=", "Less Than or Equal"),
    0x01EC: ("AND>=", "Greater Than or Equal"),
}

# Application instructions (first word)
APPLICATION_INSTRUCTIONS = {
    0x0028: ("MOV", "Move"),
    0x1028: ("MOVP", "Pulsed Move"),
    0x0038: ("ADD", "Add"),
    0x1038: ("ADDP", "Pulsed Add"),
    0x003A: ("SUB", "Subtract"),
    0x103A: ("SUBP", "Pulsed Subtract"),
    0x003C: ("MUL", "Multiply"),
    0x103C: ("MULP", "Pulsed Multiply"),
    0x003E: ("DIV", "Divide"),
    0x103E: ("DIVP", "Pulsed Divide"),
}

# Program control instructions (first word)
PROGRAM_CONTROL_INSTRUCTIONS = {
    0x0010: ("CJ", "Conditional Jump"),
    0x0012: ("CALL", "Subroutine Call"),
}

# Timer/Counter instructions (first word)
TIMER_COUNTER_INSTRUCTIONS = {
    0x000C: ("RST T/C", "Reset Timer/Counter"),
}

# Label instruction
LABEL_INSTRUCTION = 0xB0  # High byte for label instruction

# Operand type mapping
OPERAND_TYPES = {
    0x80: "K",    # 16-bit constant
    0x82: "D",    # Data Register
    0x84: "Kn",   # Bit-device group
    0x86: "T/C",  # Timer/Counter value
    0x88: "P",    # Pointer/Label
}

def decode_operand(words: List[int], index: int) -> Tuple[str, int]:
    """
    Decode an operand from the instruction words.
    Returns the operand string and the number of words consumed.
    """
    if index >= len(words):
        return "???", 0
    
    word1 = words[index]
    operand_type = (word1 >> 8) & 0xFF
    low_byte = word1 & 0xFF
    
    if operand_type not in OPERAND_TYPES:
        return f"Unknown({word1:04X})", 1
    
    # Need at least one more word for the operand
    if index + 1 >= len(words):
        return f"{OPERAND_TYPES[operand_type]}???", 1
    
    word2 = words[index + 1]
    
    if operand_type == 0x80:  # K constant
        value = (word2 << 8) | low_byte
        return f"K{value}", 2
    elif operand_type == 0x82:  # D register
        addr = (word2 << 8) | low_byte
        return f"D{addr}", 2
    elif operand_type == 0x84:  # Bit-device group
        # This is a simplification - actual decoding is more complex
        return f"K{word2}M{low_byte}", 2
    elif operand_type == 0x86:  # Timer/Counter value
        if low_byte == 0x06:  # Timer
            return f"T{word2}", 2
        elif low_byte == 0x0E:  # Counter
            return f"C{word2}", 2
        else:
            return f"T/C({low_byte:02X}){word2}", 2
    elif operand_type == 0x88:  # Pointer/Label
        return f"P{low_byte}", 2
    
    return f"{OPERAND_TYPES[operand_type]}{low_byte:02X}:{word2:04X}", 2

def decode_extended_bit_operand(word: int) -> str:
    """Decode the operand for extended bit instructions."""
    high_byte = (word >> 8) & 0xFF
    low_byte = word & 0xFF
    
    if high_byte >= 0xA8 and high_byte <= 0xAD:
        # M relays M2048 and higher
        base = 2048 + (high_byte - 0xA8) * 256
        return f"M{base + low_byte}"
    elif high_byte >= 0x80 and high_byte <= 0x83:
        # S relays S512 and higher
        base = 512 + (high_byte - 0x80) * 256
        return f"S{base + low_byte}"
    else:
        return f"Unknown({high_byte:02X}{low_byte:02X})"

def decode_instruction(words: List[int], index: int) -> Tuple[str, int]:
    """
    Decode an instruction starting at the given index in the words list.
    Returns the disassembled instruction string and the number of words consumed.
    """
    if index >= len(words):
        return "End of program", 0
    
    word = words[index]
    
    # Check for special single-word instructions
    if word in SPECIAL_INSTRUCTIONS:
        instr, _, desc = SPECIAL_INSTRUCTIONS[word]
        return f"{instr}", 1
    
    # Check for stack and logic block instructions
    if word in STACK_LOGIC_INSTRUCTIONS:
        instr, _, desc = STACK_LOGIC_INSTRUCTIONS[word]
        return f"{instr}", 1
    
    # Check for basic bit instructions
    high_byte = (word >> 8) & 0xFF
    low_byte = word & 0xFF
    
    if high_byte in BASIC_BIT_INSTRUCTIONS:
        instr, operand_type, _ = BASIC_BIT_INSTRUCTIONS[high_byte]
        return f"{instr} {operand_type}{low_byte}", 1
    
    # Check for label instruction
    if (high_byte & 0xF0) == 0xB0:
        pointer_num = low_byte
        return f"LABEL P{pointer_num}", 1
    
    # Check for multi-word instructions
    if index + 1 >= len(words):
        return f"Unknown({word:04X})", 1
    
    # Extended bit instructions
    if word in EXTENDED_BIT_INSTRUCTIONS:
        if index + 1 >= len(words):
            return f"{EXTENDED_BIT_INSTRUCTIONS[word][0]} Extended(???)", 1
        
        instr, desc = EXTENDED_BIT_INSTRUCTIONS[word]
        operand = decode_extended_bit_operand(words[index + 1])
        return f"{instr} {operand}", 2
    
    # Pulsed (Edge) instructions
    if word in PULSED_INSTRUCTIONS:
        if index + 1 >= len(words):
            return f"{PULSED_INSTRUCTIONS[word][0]} ???", 1
        
        instr, desc = PULSED_INSTRUCTIONS[word]
        operand = decode_extended_bit_operand(words[index + 1])
        return f"{instr} {operand}", 2
    
    # Compare instructions
    if word in COMPARE_INSTRUCTIONS:
        if index + 4 >= len(words):
            return f"{COMPARE_INSTRUCTIONS[word][0]} ???", 1
        
        instr, desc = COMPARE_INSTRUCTIONS[word]
        operand1, words_used1 = decode_operand(words, index + 1)
        operand2, words_used2 = decode_operand(words, index + 1 + words_used1)
        return f"{instr} {operand1} {operand2}", 1 + words_used1 + words_used2
    
    # Application instructions
    if word in APPLICATION_INSTRUCTIONS:
        instr, desc = APPLICATION_INSTRUCTIONS[word]
        
        if instr in ["MOV", "MOVP"]:
            if index + 4 >= len(words):
                return f"{instr} ???", 1
            
            source, words_used1 = decode_operand(words, index + 1)
            dest, words_used2 = decode_operand(words, index + 1 + words_used1)
            return f"{instr} {source} {dest}", 1 + words_used1 + words_used2
        
        elif instr in ["ADD", "ADDP", "SUB", "SUBP", "MUL", "MULP", "DIV", "DIVP"]:
            if index + 6 >= len(words):
                return f"{instr} ???", 1
            
            source1, words_used1 = decode_operand(words, index + 1)
            source2, words_used2 = decode_operand(words, index + 1 + words_used1)
            dest, words_used3 = decode_operand(words, index + 1 + words_used1 + words_used2)
            return f"{instr} {source1} {source2} {dest}", 1 + words_used1 + words_used2 + words_used3
    
    # Program control instructions
    if word in PROGRAM_CONTROL_INSTRUCTIONS:
        if index + 2 >= len(words):
            return f"{PROGRAM_CONTROL_INSTRUCTIONS[word][0]} ???", 1
        
        instr, desc = PROGRAM_CONTROL_INSTRUCTIONS[word]
        operand, words_used = decode_operand(words, index + 1)
        return f"{instr} {operand}", 1 + words_used
    
    # Timer/Counter instructions
    if (word & 0xFF00) == 0x0600:  # OUT T
        if index + 2 >= len(words):
            return f"OUT T{low_byte} ???", 1
        
        timer_num = low_byte
        preset, words_used = decode_operand(words, index + 1)
        return f"OUT T{timer_num} {preset}", 1 + words_used
    
    if (word & 0xFF00) == 0x0E00:  # OUT C
        if index + 2 >= len(words):
            return f"OUT C{low_byte} ???", 1
        
        counter_num = low_byte
        preset, words_used = decode_operand(words, index + 1)
        return f"OUT C{counter_num} {preset}", 1 + words_used
    
    if word == 0x000C:  # RST T/C
        if index + 1 >= len(words):
            return "RST T/C ???", 1
        
        next_word = words[index + 1]
        high_byte = (next_word >> 8) & 0xFF
        low_byte = next_word & 0xFF
        
        if high_byte == 0x86:
            return f"RST T{low_byte}", 2
        elif high_byte == 0x8E:
            return f"RST C{low_byte}", 2
        else:
            return f"RST T/C Unknown({next_word:04X})", 2
    
    # If we couldn't decode the instruction
    return f"Unknown({word:04X})", 1

def disassemble_program(words: List[int]) -> List[Tuple[List[int], str]]:
    """
    Disassemble a program from a list of 16-bit words.
    Returns a list of tuples (instruction_words, disassembled_text).
    """
    result = []
    index = 0
    
    while index < len(words):
        start_index = index
        disassembled, words_used = decode_instruction(words, index)
        
        if words_used == 0:
            break
        
        instruction_words = words[start_index:start_index + words_used]
        result.append((instruction_words, disassembled))
        
        index += words_used
    
    return result

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
