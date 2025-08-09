# Mitsubishi FX Series PLC Programming Port Communication Protocol Overview  
This protocol is applicable to the PLC programming port and the FX-232AW module communication.  

## Communication Format  
| Command (CMD)      | Command Code | Target Device          |  
|---------------------|--------------|------------------------|  
| DEVICE READ CMD     | "0"          | X, Y, M, S, T, C, D    |  
| DEVICE WRITE CMD    | "1"          | X, Y, M, S, T, C, D    |  
| FORCE ON CMD        | "7"          | X, Y, M, S, T, C       |  
| FORCE OFF CMD       | "8"          | X, Y, M, S, T, C       |  

## Extended Command Codes  
| Command            | Code  |  
|---------------------|-------|  
| Read Configuration  | "E00" |  
| Write Configuration | "E10" |  
| Read Program        | "E01" |  
| Write Program       | "E11" |  

## Transmission Format  
- Interface: RS232C  
- Baud Rate: 9600 bps  
- Parity: Even  
- Checksum: Accumulative Sum Check  
- Character Encoding: ASCII  

## Command Codes (Hexadecimal)  
| Command | Hex Code | Description               |  
|---------|----------|---------------------------|  
| ENQ     | 05H      | Communication Request     |  
| ACK     | 06H      | PLC Positive Response     |  
| NAK     | 15H      | PLC Error Response        |  
| STX     | 02H      | Start of Message          |  
| ETX     | 03H      | End of Message            |  

## Frame Format  
`STX CMD DATA ...... DATA ETX SUM(upper) SUM(lower)`  

### Example  
**Frame:**  
`02H, 30H, 31H, 30H, 46H, 36H, 30H, 34H, 03H, 37H, 34H`  

**Interpretation:**  
- `STX, "0", "10F6", "04", ETX, "74"`  
- **Description:** Start of message, read command, address `10F6H`, `04H` bytes of data, end of message, checksum.  
- **Checksum Calculation:**  
  `SUM = CMD + ... + ETX = 30h + 31h + 30h + 46h + 36h + 30h + 34h + 03h = 74h`  

### Notes  
- If the checksum exceeds two digits, only the lower two digits are taken, converted to ASCII, and transmitted as `SUM(upper)` and `SUM(lower)`.  

---

## Example 1: FX1S PLC Program Download (11 Steps)  
### Communication Parameters:  
- Interface: RS232C  
- Baud Rate: 9600, 7-bit, Even Parity, 1 Stop Bit  

### Steps:  
1. **PC Sends:** `ENQ (05H)`  
   - If no response, retry after 1.28 x 10 ms (max 3 attempts).  
2. **PLC Responds:** `ACK (06H)`  
3. **PC Sends:** Read PLC status (`STX,"0","01E0","01",ETX,"6A"`)  
   - **PLC Responds:** `STX,"0A",ETX,"74"` (PLC paused)  
4. **PC Sends:** Read PLC model (`STX,"0","0E02","02",ETX,"6C"`)  
   - **PLC Responds:** `STX,"C256",ETX,"E3"` (FX1S model)  
5. **PC Sends:** Read PLC parameters (`STX,"0","8000","2E",ETX,"72"`)  
   - **PLC Responds:** Multiple data blocks.  
6. **PC Sends:** Write program (`STX,"1","805C","16","022400C50F00FF...",ETX,"B1"`)  
   - **PLC Responds:** `ACK`  
7. **PC Sends:** Download completion command (`STX,"B",ETX,"45"`)  
   - **PLC Responds:** `ACK`  
8. **PC Sends:** Verify downloaded data (`STX,"0","805C","16",ETX,"7A"`)  
   - **PLC Responds:** Confirmation data.  

---

## Example 2: FX1N PLC Program Download (3 Steps)  
### Steps:  
1. **PC Sends:** `ENQ`  
   - **PLC Responds:** `ACK`  
2. **PC Sends:** Read PLC model (`STX,"0","0E02","02",ETX,"6C"`)  
   - **PLC Responds:** `STX,"6266",ETX,"D7"` (FX1N model)  
3. **PC Sends:** Read PLC status (`STX,"E00","01C0","01",ETX,"DD"`)  
   - **PLC Responds:** `STX,"0A",ETX,"74"` (PLC paused)  
4. **PC Sends:** Write program (`STX,"E11","805C","06","022403C50F00",ETX,"69"`)  
   - **PLC Responds:** `ACK`  
5. **PC Sends:** Verify downloaded data (`STX,"E01","805C","06",ETX,"EF"`)  
   - **PLC Responds:** Confirmation data.  

---

**Author:** Xu Yiyi  
**Date:** June 11-12, 2009  
**Source:** ourDEV.cn (Reprint with attribution)