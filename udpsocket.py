import socket
import time
import json
from io import BytesIO
from xdrlib import Packer, Unpacker
from opendis.DataOutputStream import DataOutputStream
from opendis.dis7 import EntityStatePdu
from opendis.RangeCoordinates import *

default_entity_type = {
    "entityKind": 0,
    "domain": 0,
    "country": 0,
    "category": 0,
    "subcategory": 0,
    "specific": 0,
    "extra": 0
}

def load_mapping(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

# Get the entity type from model name
def get_entity_type(mapping, model_name):
    if (model_name not in mapping["model_name_to_entitytype"]):
        print("did not find model in mapping file")
        return default_entity_type
    else:
        return mapping["model_name_to_entitytype"].get(model_name, None)

def load_config(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

mapping = load_mapping("dis-mapping.json")


# UDP Server Setup
config = load_config("configuration.json")
udp_config = config["udp_config"]
pdu_entity_ids = config["pdu_entity_ids"]

# Print UDP configuration
print(f"Listening on {udp_config['listening_ip']}:{udp_config['listening_port']}")
if udp_config["is_multicast"]:
    print(f"Multicast Group: {udp_config['multicast_group']}")
else:
    print(f"Unicast Address: {udp_config['unicast_address']}")

# setup from configurtion file 
UDP_IP = udp_config['listening_ip']
UDP_PORT = udp_config['listening_port']
MULTICAST_GROUP = udp_config['multicast_group']
UNICAST_ADDRESS = udp_config['unicast_address']
IS_MULTICAST = udp_config['is_multicast']  # Toggle between multicast and singlecast
PDU_PORT = udp_config['pdu_port']  # Port for sending PDUs

# Setup Sockets
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind((UDP_IP, UDP_PORT))

udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
if IS_MULTICAST:
    udp_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

gps = GPS()  # Conversion helper

print(f"Listening for UDP packets on {UDP_IP}:{UDP_PORT}")


# Function to pack data using XDR
def pack_flightgear_data(data):
    packer = Packer()
    packer.pack_fstring(4, data['magic'])
    packer.pack_uint(data['version'])
    packer.pack_uint(data['msg_id'])
    packer.pack_uint(data['msg_len'])
    packer.pack_uint(data['range'])
    packer.pack_uint(data['port'])
    packer.pack_fstring(8, data['callsign'])
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
    parsed_data['magic'] = unpacker.unpack_fstring(4)
    parsed_data['version'] = unpacker.unpack_uint()
    parsed_data['msg_id'] = unpacker.unpack_uint()
    parsed_data['msg_len'] = unpacker.unpack_uint()
    parsed_data['range'] = unpacker.unpack_uint()
    parsed_data['port'] = unpacker.unpack_uint()
    parsed_data['callsign'] = unpacker.unpack_fstring(8)
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

# Function to create and send a PDU
def send_pdu(parsed_data):
    pdu = EntityStatePdu()
    # set from configuration file 
    pdu.entityID.entityID = pdu_entity_ids['entityID']
    pdu.entityID.siteID = pdu_entity_ids['siteID']
    pdu.entityID.applicationID = pdu_entity_ids['applicationID']
    pdu.marking.setString(parsed_data['callsign'].decode('utf-8').rstrip('\x00'))  # Callsign

    # Must be set due to library bugs
    pdu.pduType = 1
    pdu.pduStatus = 0
    pdu.entityAppearance = 0
    pdu.capabilities = 0

    # Entity type
    # use modelname to acces mapping file to get these 7 values
    model_name = parsed_data['model_name'].decode('utf-8').rstrip('\x00') 
    model_name = model_name.split('/')[1]
    print(model_name) # use to print the model name to add to mapping file because the name from multiplayer is not the same as the one displayed in the launcher
    entityType = get_entity_type(mapping, model_name)
    pdu.entityType.entityKind = entityType['entityKind']
    pdu.entityType.domain = entityType['domain']
    pdu.entityType.country = entityType['country']
    pdu.entityType.category = entityType['category']
    pdu.entityType.subcategory = entityType['subcategory']
    pdu.entityType.specific = entityType['specific']
    pdu.entityType.extra = entityType['extra']

    # Location and orientation
    pdu.entityLocation.x = parsed_data['pos_x']
    pdu.entityLocation.y = parsed_data['pos_y']
    pdu.entityLocation.z = parsed_data['pos_z']
    pdu.entityOrientation.phi = parsed_data['ori_x']
    pdu.entityOrientation.theta = parsed_data['ori_y']
    pdu.entityOrientation.psi = parsed_data['ori_z']

    # Linear velocity
    pdu.entityLinearVelocity.x = parsed_data['vel_x']
    pdu.entityLinearVelocity.y = parsed_data['vel_y']
    pdu.entityLinearVelocity.z = parsed_data['vel_z']


    # Serialize PDU
    memory_stream = BytesIO()
    output_stream = DataOutputStream(memory_stream)
    pdu.serialize(output_stream)
    data = memory_stream.getvalue()

    # Send the PDU
    destination = (MULTICAST_GROUP if IS_MULTICAST else UNICAST_ADDRESS, PDU_PORT)
    udp_socket.sendto(data, destination)
    print(f"Sent PDU: {len(data)} bytes to {destination}")

# Process incoming packets and send PDU
while True:
    data, addr = sock.recvfrom(2048)
    print(f"\nReceived message from {addr}")
    parsed_data = unpack_flightgear_data(data)
    send_pdu(parsed_data)
    
    try:
        parsed_data = unpack_flightgear_data(data)
        send_pdu(parsed_data)
    except Exception as e:
        print(f"Error processing data: {e}")



# compile the code to be usable on linux and windows

"""
steps:
version control mit github etc angucken das man das project einfach clonen kann
reverse also das ich dis empfange und dann mit einer mapping datei bei mir in flightgear andere model sehe



zukunft:
additional data like fuel
over datapdu oder commentpdu
"""