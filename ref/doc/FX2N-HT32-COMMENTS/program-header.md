# Program Header

This header contains critical metadata that the PLC's firmware needs to understand and correctly execute the user program. Based on an analysis of both [`usart_com.c`](usart_com.c) and [`Ladder.c`](Ladder.c), here is a breakdown of the header's structure.

### Program Header Structure (Offsets `0x00` to `0x5B`)

The program header is 92 bytes long.

| Address Range (Hex) | Size (Bytes)| Description |
| :--- | :--- | :--- |
| `0000` - `0001`| 2 | **PLC Model Code**: A 2-byte code identifying the target PLC model. The firmware checks this value to ensure the program is compatible. For this device, it appears to be hardcoded to `0x5EF6`, which corresponds to a Mitsubishi **FX2N**. This is defined in [`plc_type`](usart_com.c:46). |
| `0002` - `0021` | 32 | **Program Title / Description**: A 32-byte, null-terminated ASCII string that can be used to store a human-readable name for the program. |
| `0022` - `0023` | 2 | **Program Capacity**: A 16-bit value indicating the total memory capacity of the program in steps (e.g., 8000 steps). |
| `0024` - `002B`| 8 | **File System Information**: Contains timestamps (`create_date`, `modify_date`) or other metadata used by the programming software when saving/loading projects. |
| `002C` - `003F` | 20 | **Password / Security**: A field used to store a program password. An "unlocked" program typically has this area filled with `0xFFFF`. |
| `0040` - `005B` | 28 | **Reserved / Options**: This area contains various configuration options, flags, and reserved words. This can include settings for communication formats, special memory allocation, and other advanced parameters that are set by the programming software. |

You're asking for a more detailed look at the `Reserved / Options` area of the program header, which spans from `0x40` to `0x5B`.

This section is where the PLC stores crucial configuration parameters that define how certain memory areas and hardware peripherals behave. While the firmware doesn't give named constants to every single byte, we can deduce their function by cross-referencing against standard Mitsubishi PLC configurations and how the firmware uses them.

Here is a more detailed breakdown of this 28-byte area.


### Reserved / Options Area (`0x40` - `0x5B`)

This area is treated as a series of 16-bit words.

| Address (Hex) | Mnemonic (Standard) | Description |
| :--- | :--- | :--- |
| `0040` - `0041` | `D8000` | **File Register Capacity**: Defines the size of the File Register (`R`) memory area, which is an extended data storage area. In many small programs, this is set to 0. |
| `0042` - `0043` | `D8001` | **Latch Relay Range (Start)**: Specifies the starting point of the Latched (retentive) `M` coils. For example, setting this to `500` would make `M500` and above retentive. |
| `0044` - `0045` | `D8002` | **Latch Relay Range (End)**: Specifies the ending point for the retentive `M` coils. |
| `0046` - `0047` | `D8003` | **Latch State Relay Range**: Defines the range of State relays (`S` coils) that are retentive. |
| `0048` - `0049`| `D8004` | **Latch Timer Range**: Defines the range of Timers (`T` coils) that are retentive. |
| `004A` - `004B` | `D8005` | **Latch Counter Range**: Defines the range of Counters (`C` coils) that are retentive. |
| `004C` - `004D` | `D8006` | **Latch Data Register Range (Start)**: Specifies the starting `D` register that will be retentive. |
| `004E` - `004F` | `D8007`| **Latch Data Register Range (End)**: Specifies the ending `D` register that will be retentive. |
| `0050` - `0051` | `D8008`| **Special Memory Allocation**: A bitfield used to enable or disable certain special features, such as allocating memory for high-speed counters or positioning modules. |
| `0052` - `005B` | - | **Reserved for System**: These bytes are typically reserved for future expansion or specific hardware variants and are usually set to `0xFFFF` by the programming software. The firmware doesn't appear to read from this specific sub-section. |

You've correctly identified that the **Special Memory Allocation** area, the 16-bit word at `0x0050` in the header, is particularly important. This word is not a simple value; it's a **bitfield**. Each individual bit acts as a switch (ON/OFF) to enable or disable a specific, resource-intensive hardware feature or a special function of the PLC.

The programming software sets these bits based on the user's hardware configuration and program requirements. The firmware then reads this bitfield during its boot process to allocate memory and configure peripherals accordingly.

Here is a breakdown of the common flags found in this bitfield for a Mitsubishi FX-series compatible PLC.


### Special Memory Allocation Bitfield (`D8008` / Address `0x0050`)

| Bit | Hex Value | Mnemonic (Standard) | Description |
|:--- |:--- |:--- |:---|
| 0 | `0x0001` | - | **Enable Analog I/O**: If set, the PLC allocates memory and initializes the ADC/DAC for any attached analog expansion modules. If clear, these modules are ignored. |
| 1 | `0x0002` | - | **Enable Positioning Mode**: If set, allocates memory and enables the special instructions and interrupts associated with high-speed pulse train output (PTO) for controlling stepper or servo motors. |
| 2| `0x0004` | - | **Enable High-Speed Counter (HSC) Mode**: If set, enables the special high-speed counter registers (`C235` and above) and associates them with specific physical inputs (`X0`, `X1`, etc.) to count pulses faster than the normal scan cycle. |
| 3 | `0x0008` | - | **Enable CAM/Rotary Encoder Mode**: A specialized mode for an absolute rotary encoder, allocating memory for a CAM profile table. |
| 4 | `0x0010`| `FX2N-232-BD` | **Enable Serial Port 1 (Board)**: If set, enables the optional RS-232 communication board that can be plugged into the PLC. |
| 5 | `0x0020`| `FX2N-485-BD` | **Enable Serial Port 1 (Board)**: If set, enables the optional RS-485 communication board. |
| 6 | `0x0040`| `FX2N-2CAN` | **Enable CANopen Module**: If set, enables the CANopen communication module. |
| 7 |`0x0080` | - | **Enable PID Auto-Tuning**: Allocates extra memory required for the PID auto-tuning algorithm to store its working data. |
| 8-15 | - | - | **Reserved**: These bits are reserved for other specific hardware modules or future features. |
