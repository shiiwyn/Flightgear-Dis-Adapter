import socket
import time
import json
from io import BytesIO
from xdrlib import Packer, Unpacker
from opendis.DataOutputStream import DataOutputStream
from opendis.DataInputStream import DataInputStream
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

def entity_type_to_string(entity_type):
    """Convert entityType dictionary or PDU entityType to a string key."""
    return f"{entity_type.entityKind},{entity_type.domain},{entity_type.country}," \
           f"{entity_type.category},{entity_type.subcategory},{entity_type.specific},{entity_type.extra}"


def get_model_name_from_entity(mapping, pdu):
    """Retrieve the model name from entityType."""
    entity_key = entity_type_to_string(pdu.entityType)
    return mapping["entitytype_to_model_name"].get(entity_key, {"modelName": "unknown"})["modelName"]



def load_config(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

mapping = load_mapping("dis-mapping.json")

# UDP Server Setup
config = load_config("configuration.json")
udp_config = config["udp_config"]
pdu_entity_ids = config["pdu_entity_ids"]

# Print UDP configuration
print(f"Listening on {udp_config['listening_ip']}:{udp_config['flightgear_mp_port_out']}")
if udp_config["is_multicast"]:
    print(f"Multicast Group: {udp_config['multicast_group']}")
else:
    print(f"Unicast Address: {udp_config['unicast_address']}")

# setup from configurtion file 
UDP_IP = udp_config['listening_ip']
UDP_PORT = udp_config['flightgear_mp_port_out']
MULTICAST_GROUP = udp_config['multicast_group']
UNICAST_ADDRESS = udp_config['unicast_address']
IS_MULTICAST = True # udp_config['is_multicast']  # Toggle between multicast and singlecast
PDU_PORT = udp_config['pdu_port']  # Port for sending PDUs
FLIGHTGEAR_IP = udp_config['listening_ip']
FLIGHTGEAR_PORT = udp_config['flightgear_mp_port_in']

# Setup Sockets
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind((UDP_IP, UDP_PORT))

udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
udp_socket.bind(('', PDU_PORT))

mreq = socket.inet_aton(MULTICAST_GROUP) + socket.inet_aton('0.0.0.0')
udp_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

gps = GPS()  # Conversion helper

print(f"Listening for UDP packets on {UDP_IP}:{UDP_PORT}")

def pad_packet(packet, desired_length=457):
    current_length = len(packet)
    if current_length < desired_length:
        padding = b'\x00' * (desired_length - current_length)
        return packet + padding
    return packet

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

# Function to receive DIS PDU and send to FlightGear
def receive_dis_pdu():
    while True:
        data, addr = udp_socket.recvfrom(2048)
        print(f"\nReceived DIS PDU from {addr}")
        try:
            pdu = EntityStatePdu()
            pdu.parse(DataInputStream(BytesIO(data)))

            # Convert DIS PDU to FlightGear data format
            flightgear_data = {
                'magic': b'FGFS', #FGDM
                'version': 65537, #1
                'msg_id': 7, # 1
                'msg_len': 0,
                'range': 100, 
                'port': FLIGHTGEAR_PORT, #0
                'callsign': pdu.marking.charactersString().encode('utf-8').ljust(8, b'\x00')[:8],
                'model_name': get_model_name_from_entity(mapping, pdu).encode('utf-8').ljust(96, b'\x00')[:96],  # You need to map this from DIS entity type
                'time': time.time(),
                'lag': 0.1,
                'pos_x': pdu.entityLocation.x,
                'pos_y': pdu.entityLocation.y,
                'pos_z': pdu.entityLocation.z,
                'ori_x': pdu.entityOrientation.phi,
                'ori_y': pdu.entityOrientation.theta,
                'ori_z': pdu.entityOrientation.psi,
                'vel_x': pdu.entityLinearVelocity.x,
                'vel_y': pdu.entityLinearVelocity.y,
                'vel_z': pdu.entityLinearVelocity.z,
                'av1': 0,
                'av2': 0,
                'av3': 0,
                'la1': 0,
                'la2': 0,
                'la3': 0
            }
            
            # Pack and send to FlightGear
            
            temp_data = pack_flightgear_data(flightgear_data)
            flightgear_data['msg_len'] = 457#len(temp_data)
            packed_data = pack_flightgear_data(flightgear_data)
            packed_data = pad_packet(packed_data, 457)
            sock.sendto(packed_data, (FLIGHTGEAR_IP, FLIGHTGEAR_PORT))
            print(f"Sent FlightGear data: {len(packed_data)} bytes to {FLIGHTGEAR_IP}:{FLIGHTGEAR_PORT}")
        except Exception as e:
            print(f"Error processing DIS PDU: {e}")

# Start a thread to receive DIS PDUs
import threading
dis_thread = threading.Thread(target=receive_dis_pdu)
dis_thread.start()

# Process incoming packets and send PDU
while True:
    data, addr = sock.recvfrom(2048)
    print(f"\nReceived message from {addr}")
    try:
        parsed_data = unpack_flightgear_data(data)
    except Exception as e:
        print(f"Error processing data: {e}")

