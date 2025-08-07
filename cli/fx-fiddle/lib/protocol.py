#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Protocol implementation for FX3U PLC communication.

This module provides functions and classes for communicating with an FX3U PLC
using the serial protocol described in the documentation.
"""

import time
import serial
from typing import List, Tuple, Optional


# Protocol constants
ENQ = 0x05  # Enquiry
ACK = 0x06  # Acknowledge
STX = 0x02  # Start of Text
ETX = 0x03  # End of Text


def hex_char(n: int) -> int:
    """Convert a nibble to its ASCII hex representation."""
    return 0x30 + n if n < 10 else 0x41 + n - 10


def lo_nibble(n: int) -> int:
    """Get the low nibble of a byte."""
    return n & 0x0F


def hi_nibble(n: int) -> int:
    """Get the high nibble of a byte."""
    return (n >> 4) & 0x0F


def int_to_hex_chars(value: int, num_chars: int) -> List[int]:
    """Convert an integer to a list of ASCII hex characters."""
    result = []
    for i in range(num_chars - 1, -1, -1):
        nibble = (value >> (i * 4)) & 0x0F
        result.append(hex_char(nibble))
    return result


def calculate_checksum(payload: bytes) -> bytes:
    """
    Calculate the checksum for a payload.
    
    The checksum is computed by summing all payload bytes and
    taking the lower byte, represented as 2 hex ASCII characters.
    """
    checksum = sum(payload) & 0xFF  # Take only the lower byte
    # Convert to 2 hex ASCII chars
    checksum_hi = hex_char(hi_nibble(checksum))
    checksum_lo = hex_char(lo_nibble(checksum))
    return bytes([checksum_hi, checksum_lo])


def read_response(port: serial.Serial, timeout: float = 2.0) -> bytes:
    """
    Read a response from the PLC with timeout.
    
    Args:
        port: The serial port to read from
        timeout: Maximum time to wait for a response in seconds
        
    Returns:
        The complete response as bytes
        
    Raises:
        TimeoutError: If no complete response is received within the timeout
    """
    start_time = time.time()
    response = bytearray()
    
    while time.time() - start_time < timeout:
        if port.in_waiting > 0:
            byte = port.read(1)
            response.extend(byte)
            
            # Check if we have a complete response
            # A complete response has at least STX, payload, ETX, and 2 checksum bytes
            if len(response) >= 3 and response[-3] == ETX:
                return bytes(response)
                
        time.sleep(0.01)
    
    raise TimeoutError("Timeout waiting for response from PLC")


def parse_response(response: bytes) -> Tuple[bytes, bool]:
    """
    Parse a response from the PLC.
    
    Args:
        response: The complete response as bytes
        
    Returns:
        A tuple containing (payload, checksum_valid)
        
    Raises:
        ValueError: If the response format is invalid
    """
    # Check if the response starts with STX
    if response[0] != STX:
        raise ValueError(f"Invalid response: does not start with STX, got 0x{response[0]:02X}")
    
    # Find the ETX position
    etx_pos = response.find(ETX)
    if etx_pos == -1:
        raise ValueError("Invalid response: ETX not found")
    
    # Extract the payload (between STX and ETX)
    payload = response[1:etx_pos]
    
    # Extract the checksum (after ETX)
    checksum = response[etx_pos+1:etx_pos+3]
    
    # Verify checksum (including ETX)
    checksum_data = bytearray(payload)
    checksum_data.append(ETX)
    calculated_checksum = calculate_checksum(checksum_data)
    checksum_valid = (calculated_checksum == checksum)
    
    return payload, checksum_valid


class FxProtocol:
    """Class for handling FX3U PLC protocol communication."""
    
    def __init__(self, port_name: str, baudrate: int = 38400, dry_run: bool = False, verbose: bool = False):
        """
        Initialize the protocol handler.
        
        Args:
            port_name: The name of the serial port to use
            baudrate: The baud rate to use for communication
            dry_run: If True, only print the request to console and don't send it
            verbose: If True, print detailed information about the communication
        """
        self.port_name = port_name
        self.baudrate = baudrate
        self.port = None
        self.dry_run = dry_run
        self.verbose = verbose
    
    def open(self):
        """Open the serial port."""
        if not self.dry_run:
            self.port = serial.Serial(
                self.port_name,
                baudrate=self.baudrate,
                bytesize=7,
                parity=serial.PARITY_EVEN
            )
    
    def close(self):
        """Close the serial port."""
        if self.port and self.port.is_open:
            self.port.close()
    
    def __enter__(self):
        """Context manager entry."""
        self.open()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def start_communication(self) -> bool:
        """
        Start communication with the PLC by sending ENQ and waiting for ACK.
        
        Returns:
            True if communication was successfully established, False otherwise
        """
        # If dry run, just print the ENQ and return success
        if self.dry_run:
            print("Dry run mode - ENQ that would be sent:")
            print(f"Hex bytes: 0x{ENQ:02X}")
            return True
            
        if not self.port or not self.port.is_open:
            raise ValueError("Serial port is not open")
        
        # Print verbose information if requested
        if self.verbose:
            print("Sending ENQ:")
            print(f"Hex bytes: 0x{ENQ:02X}")
        
        # Send ENQ
        self.port.write(bytes([ENQ]))
        
        # Wait for ACK
        try:
            response = self.port.read(1)
            success = bool(response) and response[0] == ACK
            
            # Print verbose information if requested
            if self.verbose:
                if success:
                    print("Received ACK:")
                    print(f"Hex bytes: 0x{ACK:02X}")
                else:
                    print(f"Did not receive ACK, got: {response.hex() if response else 'nothing'}")
            
            return success
        except Exception as e:
            if self.verbose:
                print(f"Error waiting for ACK: {str(e)}")
            return False
    
    def send_command(self, payload: bytes) -> bytes:
        """
        Send a command to the PLC and read the response.
        
        Args:
            payload: The command payload
            
        Returns:
            The response payload
            
        Raises:
            ValueError: If communication fails or response is invalid
            TimeoutError: If no response is received within the timeout
        """
        if not self.dry_run and (not self.port or not self.port.is_open):
            raise ValueError("Serial port is not open")
        
        # Create request with STX and payload
        request = bytearray([STX])
        request.extend(payload)
        
        # Calculate checksum including ETX
        checksum_data = bytearray(payload)
        checksum_data.append(ETX)
        checksum = calculate_checksum(checksum_data)
        
        # Complete the request with ETX and checksum
        request.append(ETX)
        request.extend(checksum)
        
        # If dry run, just print the request and return empty response
        if self.dry_run:
            print("Dry run mode - Request that would be sent:")
            print(f"STX: 0x{STX:02X}")
            print(f"Payload (hex): {' '.join([f'0x{b:02X}' for b in payload])}")
            print(f"Payload (ASCII): {payload.decode('ascii', errors='replace')}")
            print(f"ETX: 0x{ETX:02X}")
            print(f"Checksum: {' '.join([f'0x{b:02X}' for b in checksum])} (ASCII: {checksum.decode('ascii', errors='replace')})")
            print(f"Complete request: {' '.join([f'0x{b:02X}' for b in request])}")
            # Return empty response in dry run mode
            return b''
        
        # Print verbose information if requested
        if self.verbose:
            print("Sending request:")
            print(f"STX: 0x{STX:02X}")
            print(f"Payload (hex): {' '.join([f'0x{b:02X}' for b in payload])}")
            print(f"Payload (ASCII): {payload.decode('ascii', errors='replace')}")
            print(f"ETX: 0x{ETX:02X}")
            print(f"Checksum: {' '.join([f'0x{b:02X}' for b in checksum])} (ASCII: {checksum.decode('ascii', errors='replace')})")
            print(f"Complete request: {' '.join([f'0x{b:02X}' for b in request])}")
        
        # Send request
        assert self.port is not None, "Port should be open at this point"
        self.port.write(request)
        
        # Read response
        assert self.port is not None, "Port should be open at this point"
        response = read_response(self.port)
        
        # Parse response
        payload, checksum_valid = parse_response(response)
        
        # Print verbose information if requested
        if self.verbose:
            print("Received response:")
            print(f"STX: 0x{STX:02X}")
            print(f"Payload (hex): {' '.join([f'0x{b:02X}' for b in payload])}")
            print(f"Payload (ASCII): {payload.decode('ascii', errors='replace')}")
            print(f"ETX: 0x{ETX:02X}")
            
            # Extract the checksum from the response
            etx_pos = response.find(ETX)
            response_checksum = response[etx_pos+1:etx_pos+3]
            print(f"Checksum: {' '.join([f'0x{b:02X}' for b in response_checksum])} (ASCII: {response_checksum.decode('ascii', errors='replace')})")
            print(f"Checksum valid: {checksum_valid}")
            print(f"Complete response: {' '.join([f'0x{b:02X}' for b in response])}")
        
        if not checksum_valid:
            raise ValueError("Response checksum is invalid")
        
        return payload
    
    def read_memory(self, address: int, size: int) -> List[int]:
        """
        Read memory from the PLC.
        
        Args:
            address: The starting address to read from
            size: The number of words to read
            
        Returns:
            A list of word values read from memory
            
        Raises:
            ValueError: If communication fails or response is invalid
            TimeoutError: If no response is received within the timeout
        """
        # Start communication
        if not self.start_communication():
            raise ValueError("Failed to establish communication with PLC")
        
        # Create request payload
        # Format: 'E00' + (4 hex ASCII chars for ADDRESS) + (2 hex ASCII chars for SIZE)
        payload = bytearray(b'E00')
        
        # Add address (4 hex ASCII chars)
        address_chars = int_to_hex_chars(address, 4)
        payload.extend(address_chars)
        
        # Add size (2 hex ASCII chars)
        size_chars = int_to_hex_chars(size, 2)
        payload.extend(size_chars)
        
        # Send command and get response
        response = self.send_command(payload)
        
        # Parse response as hex ASCII chars representing words
        values = []
        for i in range(0, len(response), 4):
            if i + 4 <= len(response):
                word_str = response[i:i+4].decode('ascii')
                word_value = int(word_str, 16)
                values.append(word_value)
        
        return values