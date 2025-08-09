# PC_WRITE_Parameter() Function Description

The `PC_WRITE_Parameter()` function is a versatile write command that directs data to one of two destinations based on the provided address:

## Memory Write Destinations

### RAM Write (Address < 0x8000)
- If the high bit of the address is not set, the function performs a simple, direct write to a general-purpose RAM buffer located at `all_data`.
- These addresses map to the device's volatile memory areas, such as:
  - Special function registers
  - Timers
  - Counters
  - Data registers

### Flash Write (Address >= 0x8000)
- If the high bit of the address is set (i.e., address is 0x8000 or greater), the function initiates a write to the non-volatile on-chip Flash memory.
- This area is used to store the user's program logic (the "ladder diagram").
- Flash memory has special writing requirements, making this process more complex than a simple RAM write.

## Flash Memory and "Blocks"

Yes, the "blocks" are physical sections of the on-chip Flash memory.

### What is a Block?
- A "block" corresponds to a **Flash Page**, which in this firmware is **2048 bytes (0x800 bytes)** in size.
- The Flash memory is divided into these pages.
- They are the smallest unit that can be erased (you cannot erase a single byte - must erase the entire 2KB page).

### The RAM Buffer (`prog_write_buffer`)
- To handle the erase-before-write requirement, the firmware uses a 2KB RAM buffer called `prog_write_buffer`.
- Acts as a staging area or temporary copy of a Flash block.

## The Write Process (`PC_WRITE_Parameter`)

When a command to write to Flash is received:

1. **Block Calculation**  
   - The firmware calculates which 2KB block the target address falls into.

2. **Block Check**  
   - Checks if this is the same block it was working on previously using the `block_contol` state variables.

3. **If it's a new block**:
   - `write_block(block_contol[1])`:  
     The contents of the previous block (currently in `prog_write_buffer`) are written to Flash memory.  
     - This involves:
       1. Erasing the 2KB page
       2. Writing the new data from the buffer
   - `backup_block(block_contol[0])`:  
     The entire contents of the new target block are read from Flash into `prog_write_buffer`.  
     - Crucial because the write operation might only change a few bytes, and the rest must be preserved.

4. **Data Modification**  
   - The new data from the command is written into the appropriate location within the `prog_write_buffer` in RAM.
   - Overwrites the old data that was just read from Flash.

5. **Finalization**  
   - The data remains in the RAM buffer.
   - It is only permanently written to Flash when:
     - Another write command crosses into a new block, **OR**
     - When a "lock flash" command (`all_flash_lock()`) is sent (flushes the final buffer to Flash memory).

## Summary
`PC_WRITE_Parameter()` is the function for writing to the device's memory:
- Writes to addresses **below 0x8000** go directly to RAM.
- Writes to addresses **0x8000 and above** are buffered operations targeting 2KB "blocks" (pages) of the physical Flash memory to safely update the user's program.