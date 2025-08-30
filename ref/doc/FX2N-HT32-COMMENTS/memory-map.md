# all_data Memory Map

The following table describes the different sections of the device's RAM, which are mapped into the `all_data` memory buffer. The "Protocol Address Range" refers to the 16-bit byte address that should be used in the payload of a `PC_READ_Parameter` or `PC_WRITE_Parameter` command.

| Memory Area              | Protocol Address Range (Hex) | Word/Bit | Size       | Description |
|--------------------------|-----------------------------|----------|------------|-------------|
| M Coils (General)        | 0000 - 007F                 | Bit      | 128 Bytes  | General-purpose internal relays M0 to M1023. |
| M Coils (Special)        | 6000 - 6XXX                 | Bit      | ? Bytes    | Special relays M8000+.                       |
| Y Outputs                | 0180 - 019F                 | Bit      | 32 Bytes   | Maps to the state of the physical digital outputs, likely Y0 - Y255. |
| X Inputs                 | 0240 - 025F                 | Bit      | 32 Bytes   | Maps to the state of the physical digital inputs, likely X0 - X255. |
| C Counters (Standard)    | 0A00 - 0C00                 | Word     | 256 Words  | The current 16-bit values for standard, non-retentive counters, likely C0 to C255. |
| C Counters (Retentive)   | 0C00 - 0C63                 | Word     | 50 Words   | The current 16-bit values for retentive counters C100 to C149. |
| Special Data             | 0E00 - 0EFB                 | Word     | 126 Words  | Contains special system parameters and configuration, initialized from a constant table. Corresponds to SD (Special Device) registers in a Mitsubishi PLC. |
| T Timers (Standard)      | 1000 - 1200                 | Word     | 256 Words  | The current 16-bit values for standard, non-retentive timers, likely T0 to T255. |
| T Timers (Retentive)     | 1200 - 1263                 | Word     | 50 Words   | The current 16-bit values for retentive timers T100 to T149. |
| D Registers (Retentive)  | 43E8 - 4745                 | Word     | 450 Words  | General-purpose 16-bit data registers D500 to D949. These values are backed up to and restored from Flash. |

The standard timers and counters, like their retentive counterparts, are word-addressable. Reading or writing to them should use an even protocol address and a data size that is a multiple of 2.


## Bit Device address map

These are addresses used in bit operations

| Memory Area              | Starting Address
|--------------------------|-----------------
| M Coils (General)        | 4000
| Y Outputs                | 5E00

**Note:** The register numbers for `X` and `Y` I/O are specified in octal format.


## Address map for `memory read` command

| Address Range (Hex)  | Size       | Description                                          |
|----------------------|------------|------------------------------------------------------|
| 0x0000               | ? Bytes    | M0, M1  ...?                                         |
| 0x0098               | 2 Bytes    | X0, X1, ...                                          |
| 0x00A0               | 2 Bytes    | Y0, Y1, ...                                          |
| 0x00B0               | ? Bytes    | S bits                                               |
| 0x01E0               | ? Bytes    | Bit Changes in loop when program progresses - flags? |
| 0x0200 - 0x07FF      | ? Bytes    | Not readable                                         |
| 0x0800 - ?           | ? Bytes    | Current values of timers (and counters?) TC0, etc.   |
| 0x0900 - 0x0CFF      | ? Bytes    | Zeroes                                               |
| 0x0E00 - 0x0FFF?     | ? Bytes    | D8000+ registers                                     |
| 0x1000 - 0x4FFF      | ? Bytes    | zeroes                                               |
| 0x5000 - 0xFFFF      | ? Bytes    | Not readable                                         |


## Address map for MODBUS `read inputs` command

| Address Range (Hex)  | Size       | Description                                          |
|----------------------|------------|------------------------------------------------------|
| 0                    | 1 bits     | X0                                                   |
| 192                  | 1 bits     | X0                                                   |
| 384...               | 1 bits     | X0                                                   |


## Address map for MODBUS `read coils` command

| Address Range (Hex)  | Size       | Description                                          |
|----------------------|------------|------------------------------------------------------|
| 0                    | ? bits     | M0-M3071?                                            |
| 3072                 | 1 bits     | 1                                                    |
| 3108                 | 1 bits     | 1                                                    |
| 3502                 | 1 bits     | 1-0 every ~5sec                                      |
| 0x0C24               | 1 bits     | 1                                                    |
| 0x0ECA               | ? bits     | 6 bits change                                        |
| 0x1ECA               | ? bits     | 6 bits change                                        |
| 0x2ECA               | ? bits     | 6 bits change                                        |
| 0x3ECA               | ? bits     | 6 bits change                                        |
| 0xFECA               | ? bits     | 6 bits change                                        |
| 7872 (=8000-128)     | ? bits     | M8000+                                               |
| 7882                 | 4 bits     | 4 bits change frequently                             |
| 7886                 | 1 bits     | 1 bits change every 30s? M8014                       |
| 7900+                | ? bits     | 0 and 1s                                             |

* S, Y, X bits not accessible

## Address map for MODBUS `read holding-registers` command

| Address Range (Hex)  | Size       | Description                                          |
|----------------------|------------|------------------------------------------------------|
|   200                | 1 words    | 200                                                  |
|  4096 (0x1000)       | ? words    | Current values of timers TC0, etc.                   |
|  4352 (0x1100)       | ? words    | Current values of counters (CC0, etc.)               |
|  8000                | ? words    | zeroes                                               |
|  9100                | ? words    | changing content  (live memory?)                     |
|  9232                | ? words    | changing content                                     |
| 10333                | ? words    | changing content                                     |
| 18660+               | ? words    | unreadable                                                |


## Address map for MODBUS `read input-registers` command

Same as holding registers, even Function Code is for Holding Registers
