# FX3U protocol parser

Given the tshark dump of USB communication between host and FX3U PLC in JSON format, implement parser for its protocol.

* Parse JSON dump.
* Only consider records having `usb.capdata` field.
* If host sends request, then `usb.src` is `host`; otherwise, it is response from PLC.
* Implement protocol parsing according to the know protocol details
* Output must be in JSON lines format (json on a single line for every message)
* Add field `who` to identify, who is sending the message
  * `{"who":"host"}` for host messages  
  * `{"who":"plc"}` for PLC messages
* Add field `capdata` and put there `capdata` from the dump; join frames as necessary
  * If a frame has `STX` without matching `ETX`, then the message is split to multiple frames - join them.
* Add field `data`, containing ASCII representation of captured bytes (payload only, between STX/ETX)
* Add field `sum`, containing ASCII representation of checksum bytes
* Add field `what`, describing the type of message
  * `{"what":"ENQ"}` for `ENQ`
  * `{"what":"ACK"}` for `ACK`
  * `{"what":"DW"}` for register writes
    * Add fields for address, size, values 
  * `{"what":"DR"}` for register reads
    * Add fields for address, size, values
    * For response, also add `{"what":"DR"}` and field for values
  * `{"what":"UNK"}` for unknown messages
