import socket
import math
from xdrlib import Packer, Unpacker

# UDP Server Setup
UDP_IP = "127.0.0.1"
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind((UDP_IP, UDP_PORT))

print(f"Listening for UDP packets on {UDP_IP}:{UDP_PORT}")

# Function to pack data using XDR
def pack_flightgear_data(data):
    packer = Packer()
    # Pack header fields
    packer.pack_fstring(4, data['magic'])
    packer.pack_uint(data['version'])
    packer.pack_uint(data['msg_id'])
    packer.pack_uint(data['msg_len'])
    packer.pack_uint(data['range'])
    packer.pack_uint(data['port'])
    packer.pack_fstring(8, data['callsign'])
    
    # Pack position and other fields
    packer.pack_fstring(96, data['model_name'])
    packer.pack_double(data['time'])
    packer.pack_double(data['lag'])
    packer.pack_double(data['pos_x'])
    packer.pack_double(data['pos_y'])
    packer.pack_double(data['pos_z'])
    packer.pack_float(data['ori_x'])
    packer.pack_float(data['ori_y'])
    packer.pack_float(data['ori_z'])
    packer.pack_float(data['vel_x'])
    packer.pack_float(data['vel_y'])
    packer.pack_float(data['vel_z'])
    packer.pack_float(data['av1'])
    packer.pack_float(data['av2'])
    packer.pack_float(data['av3'])
    packer.pack_float(data['la1'])
    packer.pack_float(data['la2'])
    packer.pack_float(data['la3'])
    return packer.get_buffer()

# Function to unpack FlightGear data
def unpack_flightgear_data(data):
    unpacker = Unpacker(data)
    parsed_data = {}
    # Unpack header fields
    parsed_data['magic'] = unpacker.unpack_fstring(4)
    parsed_data['version'] = unpacker.unpack_uint()
    parsed_data['msg_id'] = unpacker.unpack_uint()
    parsed_data['msg_len'] = unpacker.unpack_uint()
    parsed_data['range'] = unpacker.unpack_uint()
    parsed_data['port'] = unpacker.unpack_uint()
    parsed_data['callsign'] = unpacker.unpack_fstring(8)
    
    # Unpack position and other fields
    parsed_data['model_name'] = unpacker.unpack_fstring(96)
    parsed_data['time'] = unpacker.unpack_double()
    parsed_data['lag'] = unpacker.unpack_double()
    parsed_data['pos_x'] = unpacker.unpack_double()
    parsed_data['pos_y'] = unpacker.unpack_double()
    parsed_data['pos_z'] = unpacker.unpack_double()
    parsed_data['ori_x'] = unpacker.unpack_float()
    parsed_data['ori_y'] = unpacker.unpack_float()
    parsed_data['ori_z'] = unpacker.unpack_float()
    parsed_data['vel_x'] = unpacker.unpack_float()
    parsed_data['vel_y'] = unpacker.unpack_float()
    parsed_data['vel_z'] = unpacker.unpack_float()
    parsed_data['av1'] = unpacker.unpack_float()
    parsed_data['av2'] = unpacker.unpack_float()
    parsed_data['av3'] = unpacker.unpack_float()
    parsed_data['la1'] = unpacker.unpack_float()
    parsed_data['la2'] = unpacker.unpack_float()
    parsed_data['la3'] = unpacker.unpack_float()
    return parsed_data

# Function to parse and process the incoming FlightGear packet
def parse_flightgear_packet(data):
    try:
        parsed_data = unpack_flightgear_data(data)
        for key, value in parsed_data.items():
            print(f"{key}: {value}")
    except Exception as e:
        print(f"Error unpacking data: {e}")

# Receive and process incoming packets
while True:
    data, addr = sock.recvfrom(2048)  # Increased buffer size if needed
    print(f"\nReceived message from {addr}")
    parse_flightgear_packet(data)
