import socket
import time

from io import BytesIO

from opendis.DataOutputStream import DataOutputStream
from opendis.dis7 import EntityStatePdu
from opendis.RangeCoordinates import *

# set from txt file
UDP_PORT = 3001
UNICAST_ADDRESS = "192.168.1.100"  # Replace with the singlecast address
MULTICAST_GROUP = "224.0.0.1"  # Replace with your desired multicast address
IS_MULTICAST = True  # Toggle between multicast and singlecast

# Setup UDP Socket
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

if IS_MULTICAST:
    # Multicast configuration
    udp_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
else:
    # For unicast, no special socket options are required
    pass

udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udpSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

gps = GPS() # conversion helper

def send():
    pdu = EntityStatePdu()
    pdu.entityID.entityID = 42 # val 1 from txt
    pdu.entityID.siteID = 17 # val 2 from txt
    pdu.entityID.applicationID = 23 # val 3 from txt
    pdu.marking.setString('Igor3d') # callsign, model name
    
    # muss hier sein wegen nem bug in der libary
    pdu.pduType = 1
    pdu.pduStatus = 0
    pdu.entityAppearance=0
    pdu.capabilities=0

    # load from mapping file
    pdu.entityType.entityKind = 0
    pdu.entityType.domain = 0
    pdu.entityType.country = 0
    pdu.entityType.category = 0
    pdu.entityType.subcategory = 0
    pdu.entityType.specific = 0
    pdu.entityType.extra = 0

    # Entity in Monterey, CA, USA facing North, no roll or pitch
    montereyLocation = gps.llarpy2ecef(deg2rad(36.6),   # longitude (radians)
                                       deg2rad(-121.9), # latitude (radians)
                                       1,               # altitude (meters)
                                       0,               # roll (radians)
                                       0,               # pitch (radians)
                                       0                # yaw (radians)
                                       )

    pdu.entityLocation.x = montereyLocation[0]
    pdu.entityLocation.y = montereyLocation[1]
    pdu.entityLocation.z = montereyLocation[2]
    pdu.entityOrientation.psi = montereyLocation[3]
    pdu.entityOrientation.theta = montereyLocation[4]
    pdu.entityOrientation.phi = montereyLocation[5]

    # additional from flightgear
    pdu.entityLinearVelocity.x = 1
    pdu.entityLinearVelocity.y = 1
    pdu.entityLinearVelocity.z = 1
    pdu.timestamp = 100


    memoryStream = BytesIO()
    outputStream = DataOutputStream(memoryStream)
    pdu.serialize(outputStream)
    data = memoryStream.getvalue()

    while True:
        if IS_MULTICAST:
            destination = (MULTICAST_GROUP, UDP_PORT)
        else:
            destination = (UNICAST_ADDRESS, UDP_PORT)

        udp_socket.sendto(data, destination)
        print("Sent {}. {} bytes".format(pdu.__class__.__name__, len(data)))
        time.sleep(60)

send()