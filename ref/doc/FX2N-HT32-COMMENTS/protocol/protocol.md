Overview
The device communicates using a half-duplex, master-slave serial protocol over a USART interface. The protocol is ASCII-based, with binary data encoded as hexadecimal strings. The device is the slave and responds to commands from a master.

Physical and Data Link Layer
Interface: Asynchronous serial (USART).
Configuration: 9600 baud, 8 data bits, no parity, 1 stop bit ("9600 8N1").
Framing & Control Characters:
STX (0x02): Start of Transmission. Every frame begins with this character. (RX_Process())
ETX (0x03): End of Text. Marks the end of the data payload, before the checksum. (RX_Process())
ENQ (0x05): Enquiry. Resets the slave's receive buffer and state, eliciting an ACK (0x06) response. Used for presence detection or synchronization. (RX_Process())
ACK (0x06): Acknowledge. Confirms successful execution of commands that don't return data (e.g., Write, Force On/Off).
NAK (0x15): Negative Acknowledge. Sent upon checksum failure or if an invalid command is received.
Packet Structure
The general structure of a frame sent from the master is:

STX <StationID> <CMD> <PAYLOAD> ETX <CHECKSUM>

STX: The 0x02 character.
StationID: A single ASCII character that is not used by the firmware but is part of the frame structure.
CMD: A single ASCII character representing the command code.
PAYLOAD: A variable-length string of ASCII characters representing addresses, data size, and values, encoded as hexadecimal.
ETX: The 0x03 character.
CHECKSUM: Two ASCII characters. This is the hexadecimal representation of the 8-bit sum of all bytes from <StationID> to <ETX> inclusive. The calculation can be seen in rx_data_sum().
Corrected Communication Example (Read Request)
Here is a corrected example for the master to read 2 bytes from address 0x0ECA.

Master Sends Read Command:

Frame: 0x02 '0' '0' '0' 'E' 'C' 'A' '0' '2' 0x03 '7' 'C'
STX: 0x02
StationID: '0' (example, ignored by slave)
CMD: '0' (for PC_READ_byte)
Payload: "0ECA02"
Address: "0ECA" (4 ASCII chars)
Size: "02" (2 ASCII chars)
ETX: 0x03
Checksum: "7C". This is the hex representation of the sum of the ASCII values: '0' + '0' + '0' + 'E' + 'C' + 'A' + '0' + '2' + 0x03.
Slave Responds: The slave sends back the requested data, which is the PLC type 0x5EF6.

Frame: 0x02 '5' 'E' 'F' '6' 0x03 'C' 'D'
STX: 0x02
Payload: "5EF6" (The data from 0x0ECA)
ETX: 0x03
Checksum: "CD"
Command Set
The main command dispatcher is Process_switch().

Command Char	Function	Description
'0' (0x30)	PC_READ_byte()	Reads bytes from device memory. Payload: <ADDR(4)> <SIZE(2)>
'1' (0x31)	PC_WRITE_byte()	Writes bytes to device memory. Payload: <ADDR(4)> <SIZE(2)> <DATA(2*SIZE)>
'4' (0x34)	find_end()	A simple test/ping command that returns an ACK.
'7' (0x37)	PC_FORCE_ON()	Forces a specific bit (e.g., a coil) ON. Payload: <ADDR(4)>
'8' (0x38)	PC_FORCE_OFF()	Forces a specific bit OFF. Payload: <ADDR(4)>
'B' (0x42)	all_flash_lock()	Finalizes a programming sequence by writing the last buffer to Flash and locking it.
'E' (0x45)	PC_OPTION_PROG()	Extended command gateway. The first byte of the binary payload acts as a sub-command.

Extended Commands (Sub-commands for 'E')
Sub-command (hex)	Function	Description
00	PC_READ_Parameter()	Reads from the parameter area of memory.
10	PC_WRITE_Parameter()	Writes to the parameter area.
01	PC_READ_PORG()	Reads from the program area of memory (Flash).
11	PC_WRITE_PORG()	Writes to the program area (buffered write).
77	all_flash_unlock()	Prepares the device for a programming sequence.
87	all_flash_lock()	(Same as main command 'B') Locks the flash.
41	find_data_address()	Searches for a 2-byte data pattern in Flash and returns its address.
D1	online_write_data()	Performs an "online change," inserting or overwriting code in the Flash memory.
