# FX3U Instruction Set Architecture

This document provides a detailed specification of the FX3U PLC instruction set, reverse-engineered from firmware source code and empirical testing. The goal is to describe each instruction's binary format completely, down to the bit level, to enable the implementation of a disassembler or other tooling.

## General Principles

1.  **Instruction Words**: Instructions are composed of one or more 16-bit words.
2.  **Endianness**: All 16-bit words are assumed to be in little-endian format as processed by the PLC.
3.  **Operand-Driven Opcodes**: The high byte of an instruction word often encodes both the instruction type (e.g., `LD`, `AND`) and the type of operand (e.g., `X`, `Y`, `M`).

## Common Operand Formats

### Bit Operand Identifier

Many instructions operate on a single bit from the PLC's memory. This bit is identified by an 8-bit value, which I will refer to as the "Bit Operand Identifier". This identifier is the lower 8 bits of the instruction word for most basic bit instructions.

The memory area and address are determined by the high byte of the instruction word. The 8-bit identifier then specifies the address within that memory area. For example, for an instruction operating on Inputs `X`, a value of `0x05` would refer to `X5`.

## Memory Areas

The PLC uses different memory areas for its operation. The specific memory area for an instruction is often determined by the opcode itself.

| Mnemonic | Description | Address Range | Notes |
|---|---|---|---|
| `X` | Inputs | `X0-X377` (octal) | The physical inputs to the PLC. |
| `Y` | Outputs | `Y0-Y377` (octal) | The physical outputs from the PLC. |
| `M` | Internal Relays | `M0-M7999` | General-purpose internal bits. |
| `M` (special) | Special Purpose Relays | `M8000-M8511` | Provide system status, flags, clocks. |
| `S` | Step Relays (States) | `S0-S4095` | Used for SFC (Sequential Function Chart) programming. |
| `T` | Timers | `T0-T511` | Timer coils and contacts. |
| `C` | Counters | `C0-C255` | Counter coils and contacts. |
| `D` | Data Registers | `D0-D7999` | 16-bit data registers for storing values. |
| `P` | Pointers (Labels) | `P0-P` | Labels for `CJ` and `CALL` instructions. |
| `K` | Constants | - | Decimal constants (e.g., `K100`). |
| `H` | Constants | - | Hexadecimal constants (e.g., `HFF`). |

---

## Basic Bit Instructions

These instructions are the fundamental building blocks of ladder logic, performing operations on single bits.

**Instruction Word Format (16-bit):**

| Bits 15-8 | Bits 7-0 |
|---|---|
| `Opcode / Memory Area` | `Bit Operand Identifier` |

- **Opcode / Memory Area (8 bits):** The high byte defines both the logical operation and the memory area to act upon.
- **Bit Operand Identifier (8 bits):** The low byte specifies the address of the bit within the selected memory area.

### Instruction Opcodes and Memory Area Mapping

The table below shows how the high byte maps to an instruction and memory area. The high byte is composed of two nibbles: `[I]O`. `[I]` is the instruction class, and `O` is the operand/memory area selector.

| `O` (hex) | Mnemonic | Memory Area | Notes |
|---|---|---|---|
| `0` | S | Step Relay | Step Relay |
| `4` | X | Input | Physical inputs |
| `6` | TS | Timer Status | Timer status bits |
| `8` | M | Internal Relay | Internal relays (0-999) |
| `C` | M | Internal Relay | Internal relays (1000-1999) |
| `E` | CS | Counter Status | Counter status bits |

### Instruction Classes `[I]`

The high nibble `[I]` of the opcode byte determines the instruction itself.

-   **`[I] = 2`**: `LD` (Load)
-   **`[I] = 3`**: `LDI` (Load Inverted)
-   **`[I] = 4`**: `AND`
-   **`[I] = 5`**: `ANI` (And Inverted)
-   **`[I] = 6`**: `OR`
-   **`[I] = 7`**: `ORI` (Or Inverted)
-   **`[I] = C`**: `OUT`
-   **`[I] = D`**: `SET`
-   **`[I] = E`**: `RST` (Reset)

### Addressing Note: M Relays

In the FX3U PLC, M relays are divided into different ranges:

- M0-M999: Accessed with high byte 0x28 (for LD instruction)
- M1000-M1999: Accessed with high byte 0x2C (for LD instruction)
- M2000+: Accessed using extended bit instructions

**Example: `LD X5`**

This instruction loads the state of input `X5`.

-   The mnemonic is `LD`, so `[I]` is `2`.
-   The operand is `X` (Input), so from the table, `O` is `4`.
-   The high byte of the instruction is `0x24`.
-   The bit address is `5`, so the low byte (Bit Operand Identifier) is `0x05`.
-   **Final 16-bit Instruction**: `0x2405`

## Stack and Logic Block Instructions

These instructions manipulate the internal logic stack, which is essential for evaluating parallel rungs (OR blocks) and complex expressions. The logic stack is implemented in the `process_value` variable, with each bit representing a level of the stack.

### `MPS` (Multi-Point Start)

Pushes the current logic result onto the stack. This is used to save the state of the current logic evaluation before starting a new sub-expression.

-   **Instruction Word (16-bit)**: `0xFFFA`

### `MRD` (Multi-Point Read)

Reads the value from the top of the logic stack without popping it. The current result is updated with the value of the stack top.

-   **Instruction Word (16-bit)**: `0xFFFB`

### `MPP` (Multi-Point Pop)

Pops the logic result from the top of the stack. The previous state is restored.

-   **Instruction Word (16-bit)**: `0xFFFC`

### `ORB` (OR Block)

Performs a logical OR between the current result and the result at the top of the stack, pops the stack, and stores the new result. This is used to join parallel branches.

-   **Instruction Word (16-bit)**: `0xFFF9`

### `ANB` (AND Block)

Performs a logical AND between the current result and the result at the top of the stack, pops the stack, and stores the new result. This is used to connect series blocks that were separated by an MPS.

-   **Instruction Word (16-bit)**: `0xFFF8`

### `INV` (Invert)

Inverts the current logic result.

-   **Instruction Word (16-bit)**: `0xFFFD`

## Application and Data Instructions

These instructions are enabled by the preceding logic result and often handle 16-bit or 32-bit data. They are typically encoded as multi-word instructions.

### Common Operand Encoding

Many data instructions use a common format for specifying their source and destination operands. An operand is typically 2 words (32 bits) long.

**Source/Destination Operand Word 1 (16 bits):**

| Bits 15-8 | Bits 7-0 |
|---|---|
| `Operand Type` | `Low byte of value/address` |

-   **Operand Type (8 bits):** Determines the kind of data being accessed (see table below).
-   **Low byte (8 bits):** The lower 8 bits of a constant, or an address offset.

**Source/Destination Operand Word 2 (16 bits):**

-   This word's content depends on the operand type. It often contains the high byte of a constant or address.

**Operand Types:**

| Type Byte | Mnemonic | Description |
|---|---|---|
| `0x80` | `K` | 16-bit constant. Word1(low), Word2(high). |
| `0x82` | `D` | Data Register. The full address is `Word1(low) + Word2(low)*0x100`. |
| `0x84` | `Kn` | Bit-device group (e.g., K4M0 for 16 bits from M0). The address is encoded in the words. |
| `0x86` | `T/C value` | Timer or Counter current value. Address from operand words. |
| `0x88` | `P` | Pointer/Label for program control instructions. |

#### Operand Encoding Examples

**Example 1: Constant `K1234`**

-   **Value**: `1234` decimal is `0x04D2` hex.
-   **Word 1**: `0x80D2`
    -   `0x80`: Operand type for `K` constant.
    -   `0xD2`: Low byte of the constant.
-   **Word 2**: `0x0004`
    -   This word simply contains the high byte of the constant.

**Example 2: Data Register `D10`**

-   **Address**: `10` decimal is `0x000A` hex.
-   **Word 1**: `0x820A`
    -   `0x82`: Operand type for `D` register.
    -   `0x0A`: Low byte of the register address.
-   **Word 2**: `0x0000`
    -   `0x00`: High byte of the register address.

---

### `MOV` (Move)

Moves a 16-bit value from a source `S` to a destination `D`. Executes if the preceding logic is true.

-   **Base Opcode**: `0x0028`
-   **Instruction Length**: 5 words (80 bits)

**Instruction Format:**

-   **Word 1**: `0x0028` (The MOV instruction itself).
-   **Word 2-3**: Source `S` operand, encoded as described above.
-   **Word 4-5**: Destination `D` operand, encoded as described above.

### `MOVP` (Pulsed Move)

Executes the `MOV` operation on the rising edge of the preceding logic.

-   **Base Opcode**: `0x1028`
-   **Instruction Length**: 5 words (80 bits)
-   **Format**: Same as `MOV`.

### Arithmetic Instructions

These instructions perform 16-bit or 32-bit arithmetic. They are enabled by the preceding logic condition.

#### `ADD` / `ADDP` (Add)

Adds two 16-bit signed values and stores the result. `ADDP` is the pulsed version.

-   **Base Opcodes**: `0x0038` (ADD), `0x1038` (ADDP)
-   **Instruction Length**: 7 words (112 bits)
-   **Format**:
    -   **Word 1**: Base opcode (`0x0038` or `0x1038`).
    -   **Word 2-3**: Source 1 `S1` operand.
    -   **Word 4-5**: Source 2 `S2` operand.
    -   **Word 6-7**: Destination `D` operand.

#### `SUB` / `SUBP` (Subtract)

Subtracts the second 16-bit signed value from the first and stores the result. `SUBP` is the pulsed version.

-   **Base Opcodes**: `0x003A` (SUB), `0x103A` (SUBP)
-   **Instruction Length**: 7 words (112 bits)
-   **Format**: Identical to `ADD`.

#### `MUL` / `MULP` (Multiply)

Multiplies two 16-bit signed values, producing a 32-bit result. `MULP` is the pulsed version.

-   **Base Opcodes**: `0x003C` (MUL), `0x103C` (MULP)
-   **Instruction Length**: 7 words (112 bits)
-   **Format**: Identical to `ADD`.
-   **Result**: The 32-bit result is stored in two consecutive 16-bit destination registers, `D` (low word) and `D+1` (high word). The destination operand specifies the address of `D`.

#### `DIV` / `DIVP` (Divide)

Divides the first 16-bit signed value by the second. `DIVP` is the pulsed version.

-   **Base Opcodes**: `0x003E` (DIV), `0x103E` (DIVP)
-   **Instruction Length**: 7 words (112 bits)
-   **Format**: Identical to `ADD`.
-   **Result**: The 16-bit quotient is stored in the destination register `D`, and the 16-bit remainder is stored in `D+1`.

### `CMP` (Compare)

Compares two 16-bit values and sets the logic state based on the result. This instruction is a 4-word instruction that starts a new rung of logic.

-   **Base Opcodes**:
    -   `0x01D0` (`LD=`)
    -   `0x01D2` (`LD>`)
    -   `0x01D4` (`LD<`)
    -   `0x01DA` (`LD<=`)
    -   `0x01DC` (`LD>=`)
-   **Instruction Length**: 5 words (80 bits)
-   **Format**:
    -   **Word 1**: The comparison instruction opcode.
    -   **Word 2-3**: Source 1 `S1` operand.
    -   **Word 4-5**: Source 2 `S2` operand.


### `AND CMP` (AND Compare)
Performs a comparison and ANDs the result with the current logic state.

-   **Base Opcodes**:
    -   `0x01E0` (`AND=`)
    -   `0x01E2` (`AND>`)
    -   `0x01E4` (`AND<`)
    -   `0x01EA` (`AND<=`)
    -   `0x01EC` (`AND>=`)
-   **Instruction Length**: 5 words (80 bits)
-   **Format**: Identical to `CMP`.


## Program Control Instructions

These instructions alter the flow of program execution. Jumps and calls rely on a pre-computed table of program labels.

### Program Labels (`P`) and Jump Table

The `CJ` and `CALL` instructions don't jump to a relative offset; they jump to an absolute address associated with a *Pointer* or *Label* number (`P0`, `P1`, etc.). This system works in two stages:

1.  **Label Definition**: Within the ladder program, a special instruction with opcode `0xB0PP` is used to define a label.
    -   **Instruction Word (16-bit)**: `0xB0PP`
    -   `0xB0`: Defines this as a `P` label instruction.
    -   `PP`: The 8-bit pointer number for this label (0-127). This instruction does nothing during execution; it's just a marker.
2.  **Pre-scan and Table Generation**: Before executing the ladder logic, the firmware performs a pre-scan of the entire program. It looks for all `0xB0PP` instructions and records the memory address of each one. These addresses are stored in a jump table array, indexed by the pointer number `PP`.
3.  **Execution**: When a `CJ Pn` or `CALL Pn` instruction is executed, it takes its 8-bit pointer number `n`, looks up the address in the jump table, and sets the program counter to the retrieved address.

This mechanism allows for fast, direct jumps to any labeled point in the program.

### `CJ` (Conditional Jump)

Jumps to a program label `P` if the preceding logic result is true.

-   **Base Opcode**: `0x0010`
-   **Instruction Length**: 3 words (48 bits)
-   **Format**:
    -   **Word 1**: `0x0010`
    -   **Word 2**: `0x88PP`, where `PP` is the 8-bit pointer number (label `P...`).
    -   **Word 3**: `0x8000` (This word appears to be fixed/padding).

### `CALL` (Subroutine Call)

Calls a subroutine at program label `P` if the preceding logic result is true.

-   **Base Opcode**: `0x0012`
-   **Instruction Length**: 3 words (48 bits)
-   **Format**:
    -   **Word 1**: `0x0012`
    -   **Word 2**: `0x88PP`, where `PP` is the 8-bit pointer number.
    -   **Word 3**: `0x8000`

### `RET` (Return)

Returns from a subroutine execution to the instruction following the `CALL`.

-   **Instruction Word (16-bit)**: `0xF7FF`

### `END`

Marks the end of the main program scan loop.

-   **Instruction Word (16-bit)**: `0x000F`

## Timer and Counter Instructions

### `OUT T` (Timer)

Drives a timer coil. When the preceding logic is true, the timer is enabled and counts towards its preset value. The timer's contact bit becomes true when the preset is reached.

-   **Base Opcode**: `0x06TT`
-   **Instruction Length**: 3 words (48 bits)
-   **Format**:
    -   **Word 1**: `0x06TT`, where `TT` is the timer number (0-511).
    -   **Word 2-3**: Preset value `S` operand, encoded using the common operand format (e.g., `K` or `D`).

### `OUT C` (Counter)

Drives a counter coil. When the preceding logic transitions from false to true, the counter increments. The counter's contact bit becomes true when its value reaches the preset.

-   **Base Opcode**: `0x0ETT`
-   **Instruction Length**: 3 words (48 bits)
-   **Format**:
    -   **Word 1**: `0x0ETT`, where `TT` is the counter number (0-255).
    -   **Word 2-3**: Preset value `S` operand, encoded using the common operand format.


### `RST T/C` (Reset Timer/Counter)

Resets a timer's or counter's accumulated value to zero.

-   **Base Opcode**: `0x000C`
-   **Instruction Length**: 2 words (32 bits)
-   **Format**:
    -   **Word 1**: `0x000C`
    -   **Word 2**: `0x86TT` for Timer `T` or `0x8ECC` for Counter `C`. `TT`/`CC` is the number.

## Extended and Pulsed Bit Instructions

These instructions use a two-word format to access bit operands that are outside the range of the basic instructions or to perform edge detection.

**Instruction Format (32-bit):**

-   **Word 1**: Base opcode for the extended/pulsed instruction.
-   **Word 2**: Operand Specifier, `0xYYXX`, where `YY` is the memory bank and `XX` is the offset.

### Extended Bit Instructions

These are used for `M` and `S` coils that have addresses > 1999 for M and > 499 for S.

-   **Opcodes (Word 1)**:
    -   `LD`: `0x01C2`
    -   `LDI`: `0x01C3`
    -   `AND`: `0x01C4`
    -   `ANI`: `0x01C5`
    -   `OR`: `0x01C6`
    -   `ORI`: `0x01C7`
    -   `OUT`: `0x0002`/`0x0005` (M/S)
    -   `SET`: `0x0003`/`0x0006` (M/S)
    -   `RST`: `0x0004`/`0x0007` (M/S)
-   **Operand Specifier Banks (Word 2, `YY`)**:
    -   `0xAA`: for `M2048` specifically
    -   `0xA8-0xAF`: for other `M` relays M2000 and higher.
    -   `0x80-0x87`: for `S` relays S500 and higher.

### Pulsed (Edge) Instructions

These execute based on a change in state from the previous scan.

-   **Opcodes (Word 1)**:
    -   `LDP`: `0x01CA` (Rising Edge)
    -   `LDF`: `0x01CB` (Falling Edge)
    -   `ANDP`: `0x01CC` (Rising Edge)
    -   `ANDF`: `0x01CD` (Falling Edge)
    -   `ORP`: `0x01CE` (Rising Edge)
    -   `ORF`: `0x01CF` (Falling Edge)
-   **Operand Specifier (Word 2)**: The `0xYYXX` format is the same as for basic bit instructions.
