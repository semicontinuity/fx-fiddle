# Address Handling in FORCE_ON/FORCE_OFF Commands

The address sent in a `FORCE_ON` or `FORCE_OFF` command is not a direct memory offset. It is an abstract address that encodes the device type (e.g., M, Y, X) in its upper bits. The firmware uses this to translate to a physical memory location, but this translation involves subtracting an implicit base address depending on the device type.

## How It Works
The calculation inside `PC_FORCE_ON()` is:  
`byte_offset = (protocol_address / 8)`  
`bit_in_byte = (protocol_address % 8)`  

However, this `byte_offset` is not the final offset. A hidden base address is then subtracted.

### M-Coils Example (M0)
- **Protocol Address**: You send `0x4000`  
- **Intermediate Offset**: `0x4000 / 8 = 0x800`  
- **Implicit Base Subtraction**: For M-coils (`4xxx` range), subtract base `0x800`  
- **Final Offset**: `0x800 - 0x800 = 0x00` → Targets first byte of `all_data` (M0)  

### Y-Outputs Example (Y0)
- **Protocol Address**: You send `0x5E00`  
- **Intermediate Offset**: `0x5E00 / 8 = 0xBC0`  
- **Implicit Base Subtraction**: For Y-outputs, subtract base `0xA40`  
- **Final Offset**: `0xBC0 - 0xA40 = 0x180` → Correctly targets Y-output buffer  