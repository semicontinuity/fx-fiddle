# Device Communication Protocol


## Overview

The device communicates using a half-duplex, master-slave serial protocol over a USART interface. The protocol is ASCII-based, with binary data encoded as hexadecimal strings. The device is the slave and responds to commands from a master.


## Physical and Data Link Layer
- 
- **Interface**: Asynchronous serial (USART)
- **Configuration**: 9600 baud, 8 data bits, no parity, 1 stop bit ("9600 8N1")
- **Framing & Control Characters**:
  - `STX (0x02)`: Start of Transmission. Every frame begins with this character. (RX_Process())
  - `ETX (0x03)`: End of Text. Marks the end of the data payload, before the checksum. (RX_Process())
  - `ENQ (0x05)`: Enquiry. Resets the slave's receive buffer and state, eliciting an ACK (0x06) response. Used for presence detection or synchronization. (RX_Process())
  - `ACK (0x06)`: Acknowledge. Confirms successful execution of commands that don't return data (e.g., Write, Force On/Off).
  - `NAK (0x15)`: Negative Acknowledge. Sent upon checksum failure or if an invalid command is received.


## Packet Structure

The general structure of a frame sent from the master is:

```
STX <StationID> <CMD> <PAYLOAD> ETX <CHECKSUM>
```


- **STX**: The `0x02` character
- **StationID**: A single ASCII character (unused by firmware but part of frame structure)
- **CMD**: A single ASCII character representing the command code
- **PAYLOAD**: Variable-length string of ASCII characters (addresses, data size, values) encoded as hexadecimal
- **ETX**: The `0x03` character
- **CHECKSUM**: Two ASCII characters representing the 8-bit sum (hexadecimal) of all bytes from `<StationID>` to `<ETX>` inclusive (see `rx_data_sum()`)


### Communication Example (Read Request)

**Master Sends Read Command**:

```
0x02 '0' '0' '0' 'E' 'C' 'A' '0' '2' 0x03 '7' 'C'
```

- STX: `0x02`
- StationID: `'0'` (example, ignored by slave)
- CMD: `'0'` (for `PC_READ_byte`)
- Payload: `"0ECA02"`
  - Address: `"0ECA"` (4 ASCII chars)
  - Size: `"02"` (2 ASCII chars)
- ETX: `0x03`
- Checksum: `"7C"` (hex sum of ASCII values: `'0' + '0' + '0' + 'E' + 'C' + 'A' + '0' + '2' + 0x03`)

**Slave Responds** (with PLC type `0x5EF6`):

```
0x02 '5' 'E' 'F' '6' 0x03 'C' 'D'
```

- STX: `0x02`
- Payload: `"5EF6"` (data from `0x0ECA`)
- ETX: `0x03`
- Checksum: `"CD"`


## Command Set

The main command dispatcher is `Process_switch()`.

| Command Char | Function           | Description                                                                 |
|--------------|--------------------|-----------------------------------------------------------------------------|
| `'0' (0x30)` | `PC_READ_byte()`   | Reads bytes from device memory. Payload: `<ADDR(4)> <SIZE(2)>`              |
| `'1' (0x31)` | `PC_WRITE_byte()`  | Writes bytes to device memory. Payload: `<ADDR(4)> <SIZE(2)> <DATA(2*SIZE)>`|
| `'4' (0x34)` | `find_end()`       | Test/ping command that returns an ACK                                       |
| `'7' (0x37)` | `PC_FORCE_ON()`    | Forces a specific bit ON. Payload: `<ADDR(4)>`                              |
| `'8' (0x38)` | `PC_FORCE_OFF()`   | Forces a specific bit OFF. Payload: `<ADDR(4)>`                             |
| `'B' (0x42)` | `all_flash_lock()` | Finalizes programming by writing last buffer to Flash and locking it        |
| `'E' (0x45)` | `PC_OPTION_PROG()` | Extended command gateway (first byte of payload acts as sub-command)        |


### Extended Commands (Sub-commands for 'E')

| Sub-command (hex) | Function                 | Description                                                                 |
|-------------------|--------------------------|-----------------------------------------------------------------------------|
| `00`             | `PC_READ_Parameter()`    | Reads from parameter area of memory                                         |
| `10`             | `PC_WRITE_Parameter()`   | Writes to parameter area                                                    |
| `01`             | `PC_READ_PORG()`         | Reads from program area (Flash)                                             |
| `11`             | `PC_WRITE_PORG()`        | Writes to program area (buffered write)                                     |
| `77`             | `all_flash_unlock()`     | Prepares device for programming sequence                                    |
| `87`             | `all_flash_lock()`       | Same as main command 'B' (locks flash)                                      |
| `41`             | `find_data_address()`    | Searches for 2-byte data pattern in Flash and returns address               |
| `D1`             | `online_write_data()`    | Performs "online change" (inserts/overwrites code in Flash)                 |
