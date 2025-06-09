import hid
import time
import sys
from typing import Optional, Dict, Union

VID = 0x1A86  # Vendor ID for D-09A
PID = 0xE429  # Product ID

def read_ut161b_hid():
    try:
        device = hid.device()
        device.open(VID, PID)  # Open the HID device
        print(f"Connected to {device.get_product_string()}")

        # URB_INTERRUPT out	
        # HID Data: 06abcd035e01d9000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
        # hid api function hid_get_feature_report needs 1 byte at front for Report ID, seems here also needed, use 0
        request_command = [0x00, 0x06, 0xab, 0xcd, 0x03, 0x5e, 0x01, 0xd9] 
        device.write(request_command)
        
        time.sleep(0.01)  # Small delay to allow response

        # Read response
        response = device.read(64)  # Read up to 64 bytes
        if response:
            #print(f"Received Data: {response}")
            # Convert to hex and format into 4 lines
            hex_lines = [bytes(response[i:i+16]).hex(" ") for i in range(0, 64, 16)]
            # Print each line
            for line in hex_lines:
                print(line)  # Uppercase for better readabilit

        else:
            print("No response received.")
        
        device.close()

    except Exception as e:
        print(f"Error: {e}")
        
    return response[0:20]


#def parse_ut161b(packet: bytes) -> Optional[Dict[str, Union[str, float]]]:
def parse_ut161b(packet: bytes):
    """
    Decodes a UNI-T UT161B multimeter HID packet.
    Returns a dictionary with 'mode', 'value', 'unit' and 'range'.
    """
    if len(packet) < 20:
        print("Error: Packet too short (expected 20 bytes)", file=sys.stderr)
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
    magic = packet[1:3]
    mode = (packet[3]<<8) | packet[4]
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

    #calc_checksum = checksum_8bit(packet[1:18])
    if checksum_8bit(packet[1:18]) != packet[19]:
        print(f"Checksum error: expected {hex(packet[19])}, got {hex(calc_checksum)}", file=sys.stderr)

    return {
        'mode': mode_map.get(mode, f"UNKNOWN (0x{mode:02x})"),
        'value': value_str,
        'unit': unit,
        'range': range_str
    }

def checksum_8bit(byte_sequence):
    return sum(byte_sequence) % 256


def main():
    """Command-line interface for parsing UT161B packets."""
    packet = read_ut161b_hid()

    result = parse_ut161b(packet)
    if result:
        print("Decoded Packet:")
        for key, val in result.items():
            print(f"{key:>6}: {val}")

if __name__ == "__main__":
    main()