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


def parse_int_or_hex(value: str) -> int:
    """Parse a string as decimal or hex (with 0x prefix)."""
    if value.lower().startswith('0x'):
        return int(value, 16)
    return int(value)


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
    
    def create_request(self, payload: bytes) -> bytes:
        """
        Create a complete request with STX, payload, ETX, and checksum.
        
        Args:
            payload: The command payload
            
        Returns:
            The complete request as bytes
        """
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
        
        return bytes(request)
    
    def print_request_info(self, request: bytes, payload: bytes, checksum: bytes):
        """
        Print detailed information about a request.
        
        Args:
            request: The complete request as bytes
            payload: The payload part of the request
            checksum: The checksum part of the request
        """
        print(f"STX: 0x{STX:02X}")
        print(f"Payload (hex): {' '.join([f'0x{b:02X}' for b in payload])}")
        print(f"Payload (ASCII): {payload.decode('ascii', errors='replace')}")
        print(f"ETX: 0x{ETX:02X}")
        print(f"Checksum: {' '.join([f'0x{b:02X}' for b in checksum])} (ASCII: {checksum.decode('ascii', errors='replace')})")
        print(f"Complete request: {' '.join([f'0x{b:02X}' for b in request])}")
    
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
        
        # Create the complete request
        request = self.create_request(payload)
        
        # Extract checksum for verbose output
        etx_pos = request.find(ETX)
        checksum = request[etx_pos+1:etx_pos+3]
        
        # If dry run, just print the request and return empty response
        if self.dry_run:
            print("Dry run mode - Request that would be sent:")
            self.print_request_info(request, payload, checksum)
            # Return empty response in dry run mode
            return b''
        
        # Print verbose information if requested
        if self.verbose:
            print("Sending request:")
            self.print_request_info(request, payload, checksum)
        
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
    
    def send_command_expect_ack(self, payload: bytes) -> bool:
        """
        Send a command to the PLC and expect an ACK response.
        
        Args:
            payload: The command payload
            
        Returns:
            True if ACK was received, False otherwise
            
        Raises:
            ValueError: If communication fails or port is not open
        """
        if not self.dry_run and (not self.port or not self.port.is_open):
            raise ValueError("Serial port is not open")
        
        # Create the complete request
        request = self.create_request(payload)
        
        # Extract checksum for verbose output
        etx_pos = request.find(ETX)
        checksum = request[etx_pos+1:etx_pos+3]
        
        # If dry run, just print the request and return success
        if self.dry_run:
            print("Dry run mode - Request that would be sent:")
            self.print_request_info(request, payload, checksum)
            return True
        
        # Print verbose information if requested
        if self.verbose:
            print("Sending request:")
            self.print_request_info(request, payload, checksum)
        
        # Send request
        assert self.port is not None, "Port should be open at this point"
        self.port.write(request)
        
        # Read response (expecting ACK)
        assert self.port is not None, "Port should be open at this point"
        response = self.port.read(1)
        
        # Check if response is ACK
        success = bool(response) and response[0] == ACK
        
        # Print verbose information if requested
        if self.verbose:
            if success:
                print("Received ACK:")
                print(f"Hex bytes: 0x{ACK:02X}")
            else:
                if response:
                    print(f"Did not receive ACK, got: 0x{response[0]:02X}")
                else:
                    print("No response received")
        
        return success
    
    def set_bit(self, address: int) -> bool:
        """
        Set a bit at the specified address.
        
        Args:
            address: The address of the bit to set
            
        Returns:
            True if the bit was successfully set, False otherwise
            
        Raises:
            ValueError: If communication fails or port is not open
        """
        # Start communication
        if not self.start_communication():
            raise ValueError("Failed to establish communication with PLC")
        
        # Create request payload
        # Format: 'E7' + (2 hex ASCII chars for low byte) + (2 hex ASCII chars for high byte)
        payload = bytearray(b'E7')
        
        # Add address in lo-endian format (low byte first, then high byte)
        low_byte = address & 0xFF
        high_byte = (address >> 8) & 0xFF
        
        # Convert to ASCII hex chars
        low_byte_chars = int_to_hex_chars(low_byte, 2)
        high_byte_chars = int_to_hex_chars(high_byte, 2)
        
        # Add to payload
        payload.extend(low_byte_chars)
        payload.extend(high_byte_chars)
        
        # Send command and expect ACK
        return self.send_command_expect_ack(payload)
    
    def clear_bit(self, address: int) -> bool:
        """
        Clear a bit at the specified address.
        
        Args:
            address: The address of the bit to clear
            
        Returns:
            True if the bit was successfully cleared, False otherwise
            
        Raises:
            ValueError: If communication fails or port is not open
        """
        # Start communication
        if not self.start_communication():
            raise ValueError("Failed to establish communication with PLC")
        
        # Create request payload
        # Format: 'E8' + (2 hex ASCII chars for low byte) + (2 hex ASCII chars for high byte)
        payload = bytearray(b'E8')
        
        # Add address in lo-endian format (low byte first, then high byte)
        low_byte = address & 0xFF
        high_byte = (address >> 8) & 0xFF
        
        # Convert to ASCII hex chars
        low_byte_chars = int_to_hex_chars(low_byte, 2)
        high_byte_chars = int_to_hex_chars(high_byte, 2)
        
        # Add to payload
        payload.extend(low_byte_chars)
        payload.extend(high_byte_chars)
        
        # Send command and expect ACK
        return self.send_command_expect_ack(payload)
    
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
                # Extract high and low bytes (each 2 ASCII chars)
                high_byte_str = response[i:i+2].decode('ascii')
                low_byte_str = response[i+2:i+4].decode('ascii')
                
                # Swap high and low bytes
                word_str = low_byte_str + high_byte_str
                
                # Convert to integer
                word_value = int(word_str, 16)
                values.append(word_value)
        
        return values
    
    def read_flash(self, address: int, size: int) -> List[int]:
        """
        Read flash memory from the PLC.
        
        Args:
            address: The starting address to read from
            size: The number of words to read
            
        Returns:
            A list of word values read from flash memory
            
        Raises:
            ValueError: If communication fails or response is invalid
            TimeoutError: If no response is received within the timeout
        """
        # Start communication
        if not self.start_communication():
            raise ValueError("Failed to establish communication with PLC")
        
        # Create request payload
        # Format: 'E01' + (4 hex ASCII chars for ADDRESS) + (2 hex ASCII chars for SIZE)
        payload = bytearray(b'E01')
        
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
                # Extract high and low bytes (each 2 ASCII chars)
                high_byte_str = response[i:i+2].decode('ascii')
                low_byte_str = response[i+2:i+4].decode('ascii')
                
                # Swap high and low bytes
                word_str = low_byte_str + high_byte_str
                
                # Convert to integer
                word_value = int(word_str, 16)
                values.append(word_value)
        
        return values
        
    def write_memory(self, address: int, values: List[int]) -> None:
        """
        Write memory to the PLC.
        
        Args:
            address: The starting address to write to
            values: The list of word values to write
            
        Raises:
            ValueError: If communication fails or response is invalid
            TimeoutError: If no response is received within the timeout
        """
        # Start communication
        if not self.start_communication():
            raise ValueError("Failed to establish communication with PLC")
        
        # Create request payload
        # Format: 'E10' + (4 hex ASCII chars for ADDRESS) + (2 hex ASCII chars for SIZE) + (2*SIZE hex ASCII chars for VALUES)
        payload = bytearray(b'E10')
        
        # Add address (4 hex ASCII chars)
        address_chars = int_to_hex_chars(address, 4)
        payload.extend(address_chars)
        
        # Add size (2 hex ASCII chars) - SIZE is in bytes (2 bytes per register)
        byte_size = len(values) * 2  # Each 16-bit register is 2 bytes
        size_chars = int_to_hex_chars(byte_size, 2)
        payload.extend(size_chars)
        
        # Add values (each value is 4 hex ASCII chars, low-endian)
        for value in values:
            # Convert to 4 hex ASCII chars (2 bytes)
            # Low byte first, then high byte (low-endian)
            low_byte = value & 0xFF
            high_byte = (value >> 8) & 0xFF
            
            # Add low byte (2 hex ASCII chars)
            low_byte_chars = int_to_hex_chars(low_byte, 2)
            payload.extend(low_byte_chars)
            
            # Add high byte (2 hex ASCII chars)
            high_byte_chars = int_to_hex_chars(high_byte, 2)
            payload.extend(high_byte_chars)
        
        # Send command and get response
        response = self.send_command(payload)
        
        # For now, we don't parse the response as it's TBD in the protocol spec
        # Just check that we got a response
        if not response and not self.dry_run:
            raise ValueError("No response received from PLC")
            
    def write_flash(self, address: int, values: List[int]) -> None:
        """
        Write flash memory to the PLC.
        
        Args:
            address: The starting address to write to
            values: The list of word values to write
            
        Raises:
            ValueError: If communication fails or response is invalid
            TimeoutError: If no response is received within the timeout
        """
        # Start communication
        if not self.start_communication():
            raise ValueError("Failed to establish communication with PLC")
        
        # Create request payload
        # Format: 'E11' + (4 hex ASCII chars for ADDRESS) + (2 hex ASCII chars for SIZE) + (2*SIZE hex ASCII chars for VALUES)
        payload = bytearray(b'E11')
        
        # Add address (4 hex ASCII chars)
        address_chars = int_to_hex_chars(address, 4)
        payload.extend(address_chars)
        
        # Add size (2 hex ASCII chars) - SIZE is in bytes (2 bytes per register)
        byte_size = len(values) * 2  # Each 16-bit register is 2 bytes
        size_chars = int_to_hex_chars(byte_size, 2)
        payload.extend(size_chars)
        
        # Add values (each value is 4 hex ASCII chars, low-endian)
        for value in values:
            # Convert to 4 hex ASCII chars (2 bytes)
            # Low byte first, then high byte (low-endian)
            low_byte = value & 0xFF
            high_byte = (value >> 8) & 0xFF
            
            # Add low byte (2 hex ASCII chars)
            low_byte_chars = int_to_hex_chars(low_byte, 2)
            payload.extend(low_byte_chars)
            
            # Add high byte (2 hex ASCII chars)
            high_byte_chars = int_to_hex_chars(high_byte, 2)
            payload.extend(high_byte_chars)
        
        # Send command and get response
        response = self.send_command(payload)
        
        # For now, we don't parse the response as it's TBD in the protocol spec
        # Just check that we got a response
        if not response and not self.dry_run:
            raise ValueError("No response received from PLC")
            
    def read_dev(self, address: int, size: int) -> List[int]:
        """
        Read device memory from the PLC.
        
        Args:
            address: The starting address to read from
            size: The number of words to read
            
        Returns:
            A list of word values read from device memory
            
        Raises:
            ValueError: If communication fails or response is invalid
            TimeoutError: If no response is received within the timeout
        """
        # Start communication
        if not self.start_communication():
            raise ValueError("Failed to establish communication with PLC")
        
        # Create request payload
        # Format: '0' + (4 hex ASCII chars for ADDRESS) + (2 hex ASCII chars for SIZE)
        payload = bytearray(b'0')
        
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
                # Extract high and low bytes (each 2 ASCII chars)
                high_byte_str = response[i:i+2].decode('ascii')
                low_byte_str = response[i+2:i+4].decode('ascii')
                
                # Swap high and low bytes
                word_str = low_byte_str + high_byte_str
                
                # Convert to integer
                word_value = int(word_str, 16)
                values.append(word_value)
        
        return values
            
    def write_dev(self, address: int, values: List[int]) -> None:
        """
        Write device memory to the PLC.
        
        Args:
            address: The starting address to write to
            values: The list of word values to write
            
        Raises:
            ValueError: If communication fails or response is invalid
            TimeoutError: If no response is received within the timeout
        """
        # Start communication
        if not self.start_communication():
            raise ValueError("Failed to establish communication with PLC")
        
        # Create request payload
        # Format: '1' + (4 hex ASCII chars for ADDRESS) + (2 hex ASCII chars for SIZE) + (2*SIZE hex ASCII chars for VALUES)
        payload = bytearray(b'1')
        
        # Add address (4 hex ASCII chars)
        address_chars = int_to_hex_chars(address, 4)
        payload.extend(address_chars)
        
        # Add size (2 hex ASCII chars) - SIZE is in bytes (2 bytes per register)
        byte_size = len(values) * 2  # Each 16-bit register is 2 bytes
        size_chars = int_to_hex_chars(byte_size, 2)
        payload.extend(size_chars)
        
        # Add values (each value is 4 hex ASCII chars, low-endian)
        for value in values:
            # Convert to 4 hex ASCII chars (2 bytes)
            # Low byte first, then high byte (low-endian)
            low_byte = value & 0xFF
            high_byte = (value >> 8) & 0xFF
            
            # Add low byte (2 hex ASCII chars)
            low_byte_chars = int_to_hex_chars(low_byte, 2)
            payload.extend(low_byte_chars)
            
            # Add high byte (2 hex ASCII chars)
            high_byte_chars = int_to_hex_chars(high_byte, 2)
            payload.extend(high_byte_chars)
        
        # Send command and get response
        response = self.send_command(payload)
        
        # For now, we don't parse the response as it's TBD in the protocol spec
        # Just check that we got a response
        if not response and not self.dry_run:
            raise ValueError("No response received from PLC")