# FX3U Protocol Reference Documentation

## Overview

This document describes the protocol parser for the Mitsubishi FX3U PLC USB communication. The parser processes tshark dump files in JSON format and extracts structured information about the communication between a host computer and the PLC.

## Input Format

The parser expects a JSON file containing tshark dump records with the following structure:
- Each record must have a `_source.layers` object
- Records must contain a `usb.capdata` field to be processed
- The `usb.src` field identifies the message source:
  - `host` indicates a message from the host computer
  - Any other value indicates a message from the PLC

## Output Format

The parser outputs JSON lines (one JSON object per line) with the following fields:

| Field | Description |
|-------|-------------|
| `who` | Message source: `"host"` or `"plc"` |
| `what` | Message type (see Command Types below) |
| `address` | Memory address in hex format (or `null` if not applicable) |
| `size` | Number of words to read/write (for register operations) |
| `values` | Array of values (for register operations) |
| `data` | ASCII representation of the payload (between STX/ETX) |
| `sum` | ASCII representation of the checksum bytes |
| `capdata` | Raw captured data in hex format |

## Command Types

The parser recognizes the following command types:

### Basic Commands

| Type | Description | Format |
|------|-------------|--------|
| `ENQ` | Enquiry | Single byte `0x05` |
| `ACK` | Acknowledge | Single byte `0x06` |
| `UNK` | Unknown | Any unrecognized format |

### Register Operations

| Type | Description | Format |
|------|-------------|--------|
| `DR` | Data Register Read | Payload starts with `E00` followed by address and size |
| `MR` | Memory Register Read | Payload starts with `E01` followed by address and size |
| `DW` | Data Register Write | Payload starts with `E10` followed by address, size, and values |
| `MW` | Memory Register Write | Payload starts with `E11` followed by address, size, and values |

### Bit Operations

| Type | Description | Format | Response |
|------|-------------|--------|----------|
| `BS` | Bit Set | Payload starts with `E7` followed by word address (lo-endian) | ACK (0x06) |
| `BC` | Bit Clear | Payload starts with `E8` followed by word address (lo-endian) | ACK (0x06) |

### System Commands

| Type | Description | Format |
|------|-------------|--------|
| `TYP` | PLC Type Query | Payload is `00E0202` |
| `VER` | PLC Version Query | Payload is `00ECA02` |

## Address Format

Addresses are represented as hex strings (e.g., "80FE", "A000"). For bit operations (BS, BC), the address is in lo-endian format, meaning the least significant byte comes first in the payload.

Example: To set a bit at address 0x4000, the payload would be "E70040" (E7 + 00 + 40).

## Message Framing

Messages are framed using:
- `STX` (0x02) - Start of Text
- `ETX` (0x03) - End of Text
- Followed by a 2-byte checksum

If a message is split across multiple frames, the parser will join them to form a complete message before processing.

## Response Handling

For request-response pairs, the PLC response will have the same `what` value as the corresponding request. This makes it easier to match requests with their responses.

Special cases:
- Responses to BS and BC commands are single-byte ACK (0x06) messages, but they are marked with the same `what` value as the request.

## Usage

```
python parse.py <input_json_file>
```

The parser will process the input file and output JSON lines to stdout.
