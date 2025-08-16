#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
FX3U PLC instruction disassembler.
"""

from typing import Tuple, List, Dict, Optional, Any

# Basic bit instruction opcodes (high byte)
# Updated for FX3U PLC based on user feedback
BASIC_BIT_INSTRUCTIONS = {
    # LD instructions (I=2)
    0x20: ("LD", "S", "Step Relay"),
    0x24: ("LD", "X", "Input"),
    0x26: ("LD", "TS", "Timer Status"),
    0x28: ("LD", "M", "Internal Relay (0-255)"),
    0x29: ("LD", "M", "Internal Relay (256-511)"),
    0x2A: ("LD", "M", "Internal Relay (512-767)"),
    0x2B: ("LD", "M", "Internal Relay (768-1023)"),
    0x2C: ("LD", "M", "Internal Relay (1024-1279)"),
    0x2D: ("LD", "M", "Internal Relay (1280-1535)"),
    0x2E: ("LD", "CS", "Counter Status"),
    0x2F: ("LD", "M8", "Special M Relay (8000+)"),
    
    # LDI instructions (I=3)
    0x30: ("LDI", "S", "Step Relay"),
    0x34: ("LDI", "X", "Input"),
    0x36: ("LDI", "TS", "Timer Status"),
    0x38: ("LDI", "M", "Internal Relay (0-255)"),
    0x39: ("LDI", "M", "Internal Relay (256-511)"),
    0x3A: ("LDI", "M", "Internal Relay (512-767)"),
    0x3B: ("LDI", "M", "Internal Relay (768-1023)"),
    0x3C: ("LDI", "M", "Internal Relay (1024-1279)"),
    0x3D: ("LDI", "M", "Internal Relay (1280-1535)"),
    0x3E: ("LDI", "CS", "Counter Status"),
    0x3F: ("LDI", "M8", "Special M Relay (8000+)"),
    
    # AND instructions (I=4)
    0x40: ("AND", "S", "Step Relay"),
    0x44: ("AND", "X", "Input"),
    0x46: ("AND", "TS", "Timer Status"),
    0x48: ("AND", "M", "Internal Relay (0-255)"),
    0x49: ("AND", "M", "Internal Relay (256-511)"),
    0x4A: ("AND", "M", "Internal Relay (512-767)"),
    0x4B: ("AND", "M", "Internal Relay (768-1023)"),
    0x4C: ("AND", "M", "Internal Relay (1024-1279)"),
    0x4D: ("AND", "M", "Internal Relay (1280-1535)"),
    0x4E: ("AND", "CS", "Counter Status"),
    
    # ANI instructions (I=5)
    0x50: ("ANI", "S", "Step Relay"),
    0x54: ("ANI", "X", "Input"),
    0x56: ("ANI", "TS", "Timer Status"),
    0x58: ("ANI", "M", "Internal Relay (0-255)"),
    0x59: ("ANI", "M", "Internal Relay (256-511)"),
    0x5A: ("ANI", "M", "Internal Relay (512-767)"),
    0x5B: ("ANI", "M", "Internal Relay (768-1023)"),
    0x5C: ("ANI", "M", "Internal Relay (1024-1279)"),
    0x5D: ("ANI", "M", "Internal Relay (1280-1535)"),
    0x5E: ("ANI", "CS", "Counter Status"),
    
    # OR instructions (I=6)
    0x60: ("OR", "S", "Step Relay"),
    0x64: ("OR", "X", "Input"),
    0x66: ("OR", "TS", "Timer Status"),
    0x68: ("OR", "M", "Internal Relay (0-255)"),
    0x69: ("OR", "M", "Internal Relay (256-511)"),
    0x6A: ("OR", "M", "Internal Relay (512-767)"),
    0x6B: ("OR", "M", "Internal Relay (768-1023)"),
    0x6C: ("OR", "M", "Internal Relay (1024-1279)"),
    0x6D: ("OR", "M", "Internal Relay (1280-1535)"),
    0x6E: ("OR", "CS", "Counter Status"),
    
    # ORI instructions (I=7)
    0x70: ("ORI", "S", "Step Relay"),
    0x74: ("ORI", "X", "Input"),
    0x76: ("ORI", "TS", "Timer Status"),
    0x78: ("ORI", "M", "Internal Relay (0-255)"),
    0x79: ("ORI", "M", "Internal Relay (256-511)"),
    0x7A: ("ORI", "M", "Internal Relay (512-767)"),
    0x7B: ("ORI", "M", "Internal Relay (768-1023)"),
    0x7C: ("ORI", "M", "Internal Relay (1024-1279)"),
    0x7D: ("ORI", "M", "Internal Relay (1280-1535)"),
    0x7E: ("ORI", "CS", "Counter Status"),
    
    # OUT instructions (I=C)
    0xC0: ("OUT", "S", "Step Relay"),
    0xC4: ("OUT", "Y", "Output"),
    0xC5: ("OUT", "Y", "Output"),  # Added for Y addressing
    0xC6: ("OUT", "T", "Timer"),
    0xC8: ("OUT", "M", "Internal Relay (0-255)"),
    0xC9: ("OUT", "M", "Internal Relay (256-511)"),
    0xCA: ("OUT", "M", "Internal Relay (512-767)"),
    0xCB: ("OUT", "M", "Internal Relay (768-1023)"),
    0xCC: ("OUT", "M", "Internal Relay (1024-1279)"),
    0xCD: ("OUT", "M", "Internal Relay (1280-1535)"),
    0xCE: ("OUT", "C", "Counter"),
    
    # SET instructions (I=D)
    0xD0: ("SET", "S", "Step Relay"),
    0xD4: ("SET", "Y", "Output"),
    0xD5: ("SET", "Y", "Output"),  # Added for Y addressing
    0xD8: ("SET", "M", "Internal Relay (0-255)"),
    0xD9: ("SET", "M", "Internal Relay (256-511)"),
    0xDA: ("SET", "M", "Internal Relay (512-767)"),
    0xDB: ("SET", "M", "Internal Relay (768-1023)"),
    0xDC: ("SET", "M", "Internal Relay (1024-1279)"),
    0xDD: ("SET", "M", "Internal Relay (1280-1535)"),
    
    # RST instructions (I=E)
    0xE0: ("RST", "S", "Step Relay"),
    0xE4: ("RST", "Y", "Output"),
    0xE5: ("RST", "Y", "Output"),  # Added for Y addressing
    0xE6: ("RST", "T", "Timer"),
    0xE8: ("RST", "M", "Internal Relay (0-255)"),
    0xE9: ("RST", "M", "Internal Relay (256-511)"),
    0xEA: ("RST", "M", "Internal Relay (512-767)"),
    0xEB: ("RST", "M", "Internal Relay (768-1023)"),
    0xEC: ("RST", "M", "Internal Relay (1024-1279)"),
    0xED: ("RST", "M", "Internal Relay (1280-1535)"),
    0xEE: ("RST", "C", "Counter"),
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

def decode_operand(words: List[int], index: int, is_timer_constant: bool = False) -> Tuple[str, int]:
    """
    Decode an operand from the instruction words.
    Returns the operand string and the number of words consumed.
    
    Args:
        words: List of instruction words
        index: Index of the current word
        is_timer_constant: Whether this operand is a timer/counter constant
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
        if is_timer_constant:
            # For timer/counter constants, the value is formed as:
            # low_byte + (word2 & 0xFF) * 0x100
            # This matches the enable_T_K() function in Ladder.c
            value = low_byte + ((word2 & 0xFF) * 0x100)
        else:
            value = (word2 << 8) | low_byte
        return f"K{value}", 2
    elif operand_type == 0x82:  # D register
        addr = (word2 << 8) | low_byte
        return f"D{addr}", 2
    elif operand_type == 0x84:  # Bit-device group
        # This is a simplification - actual decoding is more complex
        return f"K{word2}M{low_byte}", 2
    elif operand_type == 0x86:  # 16-bit register access
        hi_byte2 = (word2 >> 8) & 0xFF
        lo_byte2 = word2 & 0xFF

        if hi_byte2 == 0x80:
            # tentative
            return f"D{8000 + (low_byte + (lo_byte2 << 8))//2}", 2
        elif hi_byte2 == 0x82:
            return f"C{(low_byte + (lo_byte2 << 8))//2}", 2
        elif hi_byte2 == 0x84:
            return f"T{(low_byte + (lo_byte2 << 8))//2}", 2
        elif hi_byte2 == 0x86:
            return f"D{(low_byte + (lo_byte2 << 8))//2}", 2
        elif hi_byte2 == 0x88:
            return f"D{1000 + (low_byte + (lo_byte2 << 8))//2}", 2

    elif operand_type == 0x88:  # Pointer/Label
        return f"P{low_byte}", 2
    
    return f"{OPERAND_TYPES[operand_type]}{low_byte:02X}:{word2:04X}", 2

def decode_extended_bit_operand(word: int) -> str:
    """
    Decode the operand for extended bit instructions.
    Updated for FX3U PLC based on user feedback.
    """
    high_byte = (word >> 8) & 0xFF
    low_byte = word & 0xFF
    
    # Special case for M2048
    if high_byte == 0xAA:
        return f"M{2048 + low_byte}"
    
    # Special case for M3000
    elif high_byte == 0xAD and low_byte == 0xB8:
        return "M3000"
    
    # Special case for M8511 (max allowed M)
    elif high_byte == 0x90 and low_byte == 0xFF:
        return "M8511"
    
    # M relays M2000+
    elif high_byte >= 0xA8 and high_byte <= 0xAF:
        base = 2000 + (high_byte - 0xA8) * 256
        return f"M{base + low_byte}"
    
    # Special M relays M8000+
    elif high_byte >= 0x90 and high_byte <= 0x9F:
        base = 8000 + (high_byte - 0x90) * 32
        return f"M{base + low_byte}"
    
    # S relays S500+
    elif high_byte >= 0x80 and high_byte <= 0x87:
        base = 500 + (high_byte - 0x80) * 256
        return f"S{base + low_byte}"
    
    else:
        return f"Unknown({high_byte:02X}{low_byte:02X})"

def format_bit_address(operand_type: str, address: int) -> str:
    """Format a bit address based on operand type."""
    if operand_type == "M":
        # M addresses are decimal
        return f"M{address}"
    elif operand_type == "X" or operand_type == "Y":
        # X and Y addresses are octal (0-77)
        return f"{operand_type}{address:o}"
    elif operand_type == "S":
        return f"S{address}"
    elif operand_type == "TS":
        # Timer Status bits - format as TS0, TS1, etc.
        return f"TS{address}"
    elif operand_type == "CS":
        # Counter Status bits - format as CS0, CS1, etc.
        return f"CS{address}"
    elif operand_type == "T":
        return f"T{address}"
    elif operand_type == "C":
        return f"C{address}"
    else:
        return f"{operand_type}{address}"

def get_m_base_address(high_byte: int) -> int:
    """Get the base address for M relays based on the high byte."""
    if high_byte == 0x28:
        return 0
    elif high_byte == 0x29:
        return 256
    elif high_byte == 0x2A:
        return 512
    elif high_byte == 0x2B:
        return 768
    elif high_byte == 0x2C:
        return 1024
    elif high_byte == 0x2D:
        return 1280
    else:
        return 0

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
        
        # Special handling for M addresses
        if operand_type == "M":
            base_address = get_m_base_address(high_byte)
            return f"{instr} {format_bit_address(operand_type, base_address + low_byte)}", 1
        
        # Special handling for M8 (special M relays 8000+)
        if operand_type == "M8":
            return f"{instr} M{8000 + low_byte}", 1
        
        # Special handling for X77 (octal) which is 0x3F in hex
        if operand_type == "X" and high_byte == 0x24 and low_byte == 0x3F:
            return f"{instr} X77", 1
        
        return f"{instr} {format_bit_address(operand_type, low_byte)}", 1
    
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
            
            # For MOV instructions, K constants use the same logic as timer constants
            source, words_used1 = decode_operand(words, index + 1, is_timer_constant=True)
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
        preset, words_used = decode_operand(words, index + 1, is_timer_constant=True)
        return f"OUT T{timer_num} {preset}", 1 + words_used
    
    if (word & 0xFF00) == 0x0E00:  # OUT C
        if index + 2 >= len(words):
            return f"OUT C{low_byte} ???", 1
        
        counter_num = low_byte
        preset, words_used = decode_operand(words, index + 1, is_timer_constant=True)
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