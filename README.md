# ut161b
uni-t ut161b digital multimeter usb data read

### Scope

UNI-T 161B with UT  D09A data cable

| ![D09A data cable](img/cable_D09A.png) | ![ut161b](img/ut161b_small.png)


### Data cable D09A
serial port to HID device chip CH9329

uses built-in driver, 
HID-compliant vendor-defined device, 

VID 1A86
PID E429

### Raw HID 
simple way to receive 64byte data packets from DMM to PC

### protocol analysis
protocol to be decoded by vendor tool and wireshark

### python example 
 - open hid device 
 - send 2 request cmds
 - send measure result request
 - parse meas result response
 - close devicepython example

**output:**
````
Connected to WCH UART TO KB-MS_V1.7
request  06  ab  cd  03  4b  01  c6
response 07  ab  cd  04  ff  00  02  7b
request  06  ab  cd  03  41  01  bc
response 07  ab  cd  04  ff  00  02  7b
request  06  ab  cd  03  5e  01  d9
response 13  ab  cd  10  01  30  20  20  32  34  2e  35  34  00  05  38  34  30  03  97
Decoded meas result response:
  mode: ACmV
 value: 24.54
  unit: mV
 range: 220
````