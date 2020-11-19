# UDP Receiver kode
import socket
import struct

#UDP_IP = "192.168.137.1"
#UDP_PORT = 5005
#MESSAGE = b"ayyImao"

#print("UDP target IP: %s" % UDP_IP)
#print("UDP target port: %s" % UDP_PORT)

#sock = socket.socket(socket.AF_INET,  # Internet
#                  socket.SOCK_DGRAM)  # UDP

#sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))


UDP_IP_in = "172.26.19.9"
UDP_PORT_in = 5004

sock_in = socket.socket(socket.AF_INET,  # Internet
                  socket.SOCK_DGRAM)  # UDP
sock_in.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1)
sock_in.bind((UDP_IP_in, UDP_PORT_in))

while True:
    data, addr = sock_in.recvfrom(1024)  # buffer size is 1024 bytes
    # print as hex
    res = ''.join(format(x, '02x') for x in data)
    print("received message: ")
    print(res)

    # Read values from packet
    PosX = struct.unpack_from('d', data, 0)
    PosY = struct.unpack_from('d', data, 8)
    PosZ = struct.unpack_from('d', data, 16)
    RotX = struct.unpack_from('d', data, 24)
    RotY = struct.unpack_from('d', data, 32)
    RotZ = struct.unpack_from('d', data, 40)
    i = struct.unpack_from('Q', data, 48)
    # Print raw buffer
    print("Packet: \n Pos: ")
    print(PosX)
    print(PosY)
    print(PosZ)
    print(" Rot: ")
    print(RotX)
    print(RotY)
    print(RotZ)
    print(" PacketNo: ")
    print(i)