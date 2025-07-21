import hid
import time
import sys
#from typing import Optional, Dict, Union

VID = 0x1A86  # Vendor ID for D-09A
PID = 0xE429  # Product ID

#
# build 7 bytes request cmd, see ut161b_protocol.md
# cmd is uint16 containing request comand type
def handle_request(device: hid.device, cmd: int):
    cmd &= 0xFFFF  
    cmd0 = (cmd & 0xFF00) >> 8  # upper 8 bit
    cmd1 = cmd & 0x00FF         # lower 8 bits
    sum  = (0xab + 0xcd + cmd0 + cmd1) & 0xFFFF
    sum0 = (sum & 0xFF00) >> 8
    sum1 = sum & 0x00FF
    # hid api function hid_get_feature_report needs 1 byte at front for Report ID, seems here also needed, use 0
    request_command = [0x00, 0x06, 0xab, 0xcd, cmd0, cmd1, sum0, sum1] 
    print_packet("request ", request_command[1:])
    device.write(request_command)
    
    time.sleep(0.01)  # Small delay to allow response

    response = device.read(64)  # Read up to 64 bytes      
    return response[0:64]

#
#
def print_packet(desc: str, packet: bytes):
    length = packet[0]
    # print length+1 bytes
    disp = packet[:length+1]
    formatted = '  '.join(f'{b:02x}' for b in disp)
    print(desc, formatted)       

#
# get low and high byte of bytesum
def byte_sum_split(byte_seq):
    total = sum(byte_seq) & 0xFFFF
    low_byte = total & 0x00FF
    high_byte = (total >> 8) & 0x00FF
    return low_byte, high_byte

#
#
def parse_meas_result(packet: bytes):
    """
    Decodes a UNI-T UT161B multimeter HID packet containg meas results.
    Returns a dictionary with 'mode', 'value', 'unit' and 'range'.
    """
    if len(packet) < 20:
        print("Error: Packet too short, minimum 20bytes", file=sys.stderr)
        return None

    # Mode mappings
    mode_map = {
        0x1000: "ACV",
        0x1001: "ACmV",
        0x1002: "DCV",
        0x1003: "DCmV",
        0x1004: "FREQ",
        0x1005: "Duty",
        0x1006: "RES",
        0x1008: "Diode",
        0x1009: "CAP",
        0x100c: "DCµA",
        0x100d: "ACµA",
        0x100e: "DCmA",
        0x100f: "ACmA",
        0x1010: "DCA",
        0x1011: "ACA",
    }

    # Extract fields
    length = packet[0]
    magic  = packet[1:3]
    mode   = (packet[3]<<8) | packet[4]
    range_flag = packet[5]  # ASCII digit
    value_str = bytes(packet[6:13]).decode('ascii').strip()  # '  3.795' → '3.795'
    range_info = packet[13:15]
    unit_raw = bytes(packet[15:18]).decode('ascii')

    # set unit and range_map based on mode 
    range_map = {}
    if mode == 0x1000 or mode == 0x1002:  # ACV or DCV
        unit = "V"
        range_map = {
            0x30: "2",   
            0x31: "22",  
            0x32: "220", 
            0x33: "1000",
        }
    elif mode == 0x1001 or mode == 0x1003:  # ACmV or DCmV
        unit = "mV"
        range_map = {
            0x30: "220",   
            0x31: "1000",  # ?
        }
    elif mode == 0x1004:  # FREQ
        unit = "Hz"
        range_map = {
            0x30: "22",
        }
    elif mode == 0x1006:  # RES
        unit_map = {
            0x30: "Ω", 
            0x31: "kΩ",
            0x32: "kΩ",
            0x33: "kΩ",
            0x34: "MΩ",
            0x35: "MΩ",
        }
        unit = unit_map.get(range_flag, (f"?Ω"))
        range_map = {
            0x30: "220",
            0x31: "2",  
            0x32: "22", 
            0x33: "220",
            0x34: "2",  
            0x35: "22", 
        }
    elif mode == 0x1008:  # Diode
        unit = "V"
        range_map = {
            0x30: "2",
        }
    elif mode == 0x1009:  # CAP
        unit = "nF"
        range_map = {
            0x30: "22",
        }
    elif mode == 0x100c or mode == 0x100d:  # DCµA or ACµA
        unit = "µA"
        range_map = {
            0x30: "220",
            0x31: "2200",
        }
    elif mode == 0x100e or mode == 0x100f:  # DCmA or ACmA
        unit = "mA"
        range_map = {
            0x30: "22",
            0x31: "220",
        }
    elif mode == 0x1010 or mode == 0x1011:  # DCA or ACA
        unit = "A"
        range_map = {
            0x30: "2",
            0x31: "22",
        }
    else:
        unit = ""
        range_map = {}

    range_str = range_map.get(range_flag, (f"Range {range_flag - 0x30}", "?"))

    sum0, sum1 =  byte_sum_split(packet[1:length-1])
    if sum0 != packet[19]:
        print(f"Checksum error: expected {hex(packet[19])}, got {hex(sum0)}", file=sys.stderr)
    if sum1 != packet[18]:
        print(f"Checksum error: expected {hex(packet[18])}, got {hex(sum1)}", file=sys.stderr)


    return {
        'mode': mode_map.get(mode, f"UNKNOWN (0x{mode:02x})"),
        'value': value_str,
        'unit': unit,
        'range': range_str
    }

#########################################################################

# basic example 
# - open hid device 
# - send some request cmd
# - send measure result request , 
# - parse meas result response
# - close device
def main():
    try:
        device = hid.device()
        device.open(VID, PID)  # Open the HID device
        print(f"Connected to {device.get_product_string()}")

		# send switch light request
        resp = handle_request(device, 0x034b)
        print_packet("response", resp)
        time.sleep(0.1)     # switch light seems to need some time

		# send MAX/MIN request 
        resp = handle_request(device, 0x0341)
        print_packet("response", resp)
        time.sleep(0.1)

        # send req 035e meas result and receive packet
        resp = handle_request(device, 0x35e)
        print_packet("response", resp)

        # parse meas result
        result = parse_meas_result(resp)
        if result:
            print("Decoded meas result response:")
            for key, val in result.items():
                print(f"{key:>6}: {val}")


        device.close()

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()