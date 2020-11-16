# UDP Receiver kode
import socket
import struct

UDP_IP = "192.168.137.1"
UDP_PORT = 5005
MESSAGE = b"ayyImao"

print("UDP target IP: %s" % UDP_IP)
print("UDP target port: %s" % UDP_PORT)

sock = socket.socket(socket.AF_INET,  # Internet
                  socket.SOCK_DGRAM)  # UDP

sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))


UDP_IP_in = "172.26.50.216"
UDP_PORT_in = 5004

sock_in = socket.socket(socket.AF_INET,  # Internet
                  socket.SOCK_DGRAM)  # UDP

sock_in.bind((UDP_IP_in, UDP_PORT_in))

while True:
    data, addr = sock_in.recvfrom(1024)  # buffer size is 1024 bytes
    print("received message: %s" % data)

# Bytearray Kode
# Create a byte array of length 8
    print("Modified byte array - raw:")
    print(struct.unpack_from(d,data,0))
    # Print raw buffer

    for float in data:
        print(float)

    print("Modified byte array - string:")
    # Print the actual characters

    for float in data:
        print(chr(float))

    # Bytearray to Hex kode

    # Python3 code to demonstrate working of
    # Converting bytearray to hexadecimal string
    # Using join() + format()

    # initializing list
    test_list = [data]

    # printing original list
    print("The original string is : " + str(data))

    # using join() + format()
    # Converting bytearray to hexadecimal string
    res = ''.join(format(x, '02x') for x in data)

    # printing result
    print("The string after conversion : " + str(res))
