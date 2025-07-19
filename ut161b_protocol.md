## UT161B
### Protocol analysis

commands are sent and data received via HID data in URB interrupt frames 

#### request cmds host -> device

URB interrupt out frame 

​	total size: 91bytes , 27 USB URB , 64 HID data 

##### HID data request command

used 7 bytes (always ?)

examples: 
- get meas result [0x06, 0xab, 0xcd, 0x03, 0x5e, 0x01, 0xd9] 

| offset   | size | value (hex) | comment |
| -------- | -- | ----------- | ------- |
| 0        | 1  | 06          | len     |
| 1        | 2  | ab cd       | UNI-T header |
| 3        | 2  | 03 5e       | command type |
| 5        | 2  | 01 d9       | bytesum (1-4) |


- set MAX/MIN
##### request command types

0341	MAX/MIN

0342	exit MAX/MIN

0346	manual

0347	AUTO

034b	switch light

035e 	meas result

..tbc

#### response device ->  host

URB_INTERRUPT in frame

- 91 byte

  ​	`Frame 4389: 91 bytes on wire (728 bits), 91 bytes captured (728 bits) on interface \\.\USBPcap1, id 0*`

- 64 byte HID Data contain response data

##### response on command request
first 8 bytes seem always identical:
07abcd04ff00027b... 

##### response on meas result request
20 bytes are relevant, example data: 

###### DCV 3.795
````
13 ab cd 10 02 30 20 20 33 2e 37 39 35 01 08 30
30 30 03 99 cb f7 6b af a7 4f ff ce 7b b7 28 6b
4c f7 d9 75 5d af 79 ff 9f 75 af ef f7 7f eb d9
ff 37 db eb a7 df ef 2b ae d7 bb fd f9 f7 5f 6b
````

###### frame structure meas results
| offset | size | value (hex)          | interpretation      |
| -------| ---- | -------------------- | ------------------- |
| 0      | 1    | 13                   | length              |
| 1      | 2    | ab cd                | UNI-T header        |
| 3      | 2    | 10 02                | **mode** see next table      |
| 5      | 1    | 30                   | **range** ascii, dep on mode |
| 6      | 7    | 20 20 33 2e 37 39 35 | **value** ascii __3.795      |
| 13     | 2    | 01 08                | unclear                      |
| 15     | 3    | 30 30 30             | **sign? ** ascii             |
| 18     | 2    | 03 99                | **bytesum** (1-17)           |

###### mode value interpretation and ranges 

| mode value  |  interpretation |unit | range flags   |
| ----------- |  -------------- |---- | ------------  |
| 0x1000      | ACV             | V   | 30="2", 31="22", 32="220", 33="1000"  |
| 0x1001      | ACmV            | mV  | 30="220", 31="1000"                   |
| 0x1002      | DCV             | V   | 30="2", 31="22", 32="220", 33="1000"  |
| 0x1003      | DCmV            | mV  | 30="220", 31="1000"                   |
| 0x1004      | FREQ            | Hz  | 30="22"                               |
| 0x1005      | Duty            |     |   |
| 0x1006      | RES             |     | 30="220Ω", 31="2kΩ", 32="22kΩ", 33="220kΩ", 34="2MΩ",35="22MΩ" |
| 0x1008      | Diode           | V   | 30="2"  |
| 0x1009      | CAP             | nF  |   |
| 0x100c      | DCµA            | µA  |   |
| 0x100d      | ACµA            | µA  |   |
| 0x100e      | DCmA            | mA  |   |
| 0x100f      | ACmA            | mA  |   |
| 0x1010      | DCA             | A   |   |
| 0x1011      | ACA             | A   |   |

###### DCV -3.792
````
13 ab cd 10 02 30 20 2d 33 2e 37 39 32 01 08 30
30 31 03 a4 cb f7 6b af a7 4f ff ce 7b b7 28 6b
4c f7 d9 75 5d af 79 ff 9f 75 af ef f7 7f eb d9
ff 37 db eb a7 df ef 2b ae d7 bb fd f9 f7 5f 6b
````