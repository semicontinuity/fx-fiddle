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
