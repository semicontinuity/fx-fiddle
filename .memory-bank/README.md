The goal is to create a CLI program to work with FX3U PLC clone.
This program will communicate with PLC via serial port.


## Requirements

* Use python
  * `click` library for CLI


## Protocol description

Host and PLC exchange messages, consisting of ASCII characters.
All numbers, that are used in the messages, represented as hex uppercase characters; e.g. 254 = "FE" = [0x46, 0x45]

PLC has memory, organised into 16-bit registers.
These registers are low-endian; e.g., 77 is represented as ['4' 'D' '0 ' '0'] = [0x004d]

Some of these characters are in the 0x00-0x1F range and are used for framing:

`STX`: `0x02` Start of Text
`ETX`: `0x03` End of Text
`ENQ`: `0x05` Enquiry
`ACK`: `0x06` Acknowledge


The communication is done in the form of dialog:
HOST:
  [ `ENQ` ]
PLC:
  [ `ACK` ]
HOST:
  [ `STX` (request payload) `ETX` (checksum char 1) (checksum char 2) ]
PLC:
  [ `STX` (response payload) `ETX` (checksum char 1) (checksum char 2) ]

there may be multiple request/response pairs after `ENQ`/`ACK` pair, as necessary.

Checksum is computed as follows: all payload bytes + `ETX` are summed up, and lower 2 bytes are added as hex uppercase characters.


### Read memory command

Reads register.

Request payload = `['E' '0' '0' + (4 hex ASCII chars for ADDRESS) + (2 hex ASCII chars for SIZE)]`
Response payload = SIZE number of memory bytes (every byte is represented as 2 hex ASCII chars in the message)


### Write memory command

Writes register.

Request payload = `['E' '1' '0' + (4 hex ASCII chars for ADDRESS) + (2 hex ASCII chars for SIZE) + (2*SIZE hex ASCII chars for VALUE)]`
Response payload = TBD
