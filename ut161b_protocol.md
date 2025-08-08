## UT161B with D-09A
### Protocol analysis

Vendor tool UT161E v2.02 was used to control the device, wireshark with USBPcap1 was used to record frames.

USB source and destination to find via string search for Device 1A86 (vendor id for QinHeng Electronics)

Commands are sent and data received via HID data in URB interrupt frames 

### request cmds host -> device

URB interrupt out frame 

​	total size: 91bytes , 27 USB URB , 64 HID data 

#### HID data request command

all commands observed have length 7 byte

example: 
- get meas result [0x06, 0xab, 0xcd, 0x03, 0x5e, 0x01, 0xd9] 

| offset   | size | value (hex) | comment |
| -------- | -- | ----------- | ------- |
| 0        | 1  | 06          | len     |
| 1        | 2  | ab cd       | UNI-T header    |
| 3        | 1  | 03          | bytes to follow |
| 4        | 1  | 5e          | command type    |
| 5        | 2  | 01 d9       | bytesum (1-4)   |


#### request command types

| cmd (hex)      | interpretation |
| -------------- | -------------- |
| 41             | MAX/MIN        |
| 42             | exit MAX/MIN   |
| 46             | manual         |
| 47             | AUTO           |
| 48             | rel            |
| 4b             | switch light   |
| 4d             | Peak min/max   |
| 4e             | exit Peak      |
| 5e             | meas result    |
|                |                |
| 5f followed by | device name    |
| 30             | flush buf ?    |


### response device ->  host

URB_INTERRUPT in frame

- 91 byte

  ​	`Frame 4389: 91 bytes on wire (728 bits), 91 bytes captured (728 bits) on interface \\.\USBPcap1, id 0*`

- 64 byte HID Data contain response data

#### response on command request
almost identical
07abcd04ff00027b

#### response on device ident request
0b ab cd 08 55 54 31 36 31 42 03 03

##### frame structure
| offset | size | value (hex)          | interpretation      |
| -------| ---- | -------------------- | ------------------- |
| 0      | 1    | 0b                   | length              |
| 1      | 2    | ab cd                | UNI-T header        |
| 3      | 1    | 08                   | bytes to follow     |
| 4      | 6    | 55 54 31 36 31 42    | ascii **UT161B**    |
| 10     | 2    | 03 03                | **bytesum** (1-11)  |


#### response on meas result request
**example data 64 byte HID  (meas mode DCV, display 3.795V)** 
````
13 ab cd 10 02 30 20 20 33 2e 37 39 35 01 08 30
30 30 03 99 cb f7 6b af a7 4f ff ce 7b b7 28 6b
4c f7 d9 75 5d af 79 ff 9f 75 af ef f7 7f eb d9
ff 37 db eb a7 df ef 2b ae d7 bb fd f9 f7 5f 6b
````
relevant are first 20 byte:

##### frame structure meas results
| offset | size | value (hex)          | interpretation      |
| -------| ---- | -------------------- | ------------------- |
| 0      | 1    | 13                   | length              |
| 1      | 2    | ab cd                | UNI-T header        |
| 3      | 1    | 10                   | bytes to follow              |
| 4      | 1    | 02                   | **mode** see next table      |
| 5      | 1    | 30                   | **range** ascii, dep on mode |
| 6      | 7    | 20 20 33 2e 37 39 35 | **value** ascii __3.795      |
| 13     | 2    | 01 08                | unclear , progress?          |
| 15     | 1    | 30                   | **meas settings1** bitmask   |
| 16     | 1    | 30                   | **meas settings2** bitmask   |
| 17     | 1    | 30                   | **meas settings3** bitmask   |
| 18     | 2    | 03 99                | **bytesum** (1-17)           |

##### mode value interpretation and ranges 

| mode (hex)  |  interpretation |unit | range flags   |
| ----------- |  -------------- |---- | ------------  |
| 00          | ACV             | V   | 30="2", 31="22", 32="220", 33="1000"  |
| 01          | ACmV            | mV  | 30="220", 31="1000"                   |
| 02          | DCV             | V   | 30="2", 31="22", 32="220", 33="1000"  |
| 03          | DCmV            | mV  | 30="220", 31="1000"                   |
| 04          | FREQ            | Hz  | 30="22"                               |
| 05          | Duty            |     |   |
| 06          | RES             |     | 30="220Ω", 31="2kΩ", 32="22kΩ", 33="220kΩ", 34="2MΩ",35="22MΩ" |
| 07          | Cont            |     | 30="220Ω"            |
| 08          | Diode           | V   | 30="2"               |
| 09          | CAP             | nF  | 30="22"              |
| 0c          | DCµA            | µA  | 30="220", 31="2200"  |
| 0d          | ACµA            | µA  | 30="220", 31="2200"  |
| 0e          | DCmA            | mA  | 30="22", 31="220"    |
| 0f          | ACmA            | mA  | 30="22", 31="220"    |
| 10          | DCA             | A   | 30="2", 31="22"      |
| 11          | ACA             | A   | 30="2", 31="22"      |

