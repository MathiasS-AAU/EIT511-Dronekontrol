from math import *
import pandas as pd
import socket
import struct
import logging
import time
import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.positioning.motion_commander import MotionCommander

# File setup
file = open(r"/home/eit511/Desktop/test.csv", "w")
text = "Time,X,Y,Z,step,Yaw,latencyUDP\n"
step = 0

# DataStream Setup
UDP_IP_in = "10.0.2.15"
UDP_PORT_in = 5004
sock_in = socket.socket(socket.AF_INET,  # Internet
                        socket.SOCK_DGRAM)  # UDP
sock_in.bind((UDP_IP_in, UDP_PORT_in))
k = 0

# Crazyflie Setup
URI = 'radio://0/80/250K'
logging.basicConfig(level=logging.ERROR)
cflib.crtp.init_drivers(enable_debug_driver=False)

# Start flight
with SyncCrazyflie(URI, cf=Crazyflie(rw_cache='./cache')) as scf:
    print("Crazyflie taking off")
    with MotionCommander(scf) as mc:
        time.sleep(1)
        mc._reset_position_estimator
        time.sleep(0.1)
        print("Starting control sequence!")
        for x in range(1, 1000):
            while True:
                data, addr = sock_in.recvfrom(56)  # buffer size is 1024 bytes'
                i = struct.unpack_from('Q', data, 48)
                nowTime = int(time.time()*1000)
                latencyUDP = nowTime - i[0]
                if latencyUDP < 50:
                    print(latencyUDP)
                    break

            # print as hex
            res = ''.join(format(x, '02x') for x in data)

            # Read values from packet
            PosX = struct.unpack_from('d', data, 0)
            PosY = struct.unpack_from('d', data, 8)
            PosZ = struct.unpack_from('d', data, 16)
            RotX = struct.unpack_from('d', data, 24)
            RotY = struct.unpack_from('d', data, 32)
            RotZ = struct.unpack_from('d', data, 40)

            # Text string for printing
            text = text + i + "," + PosX + "," + PosY + "," + PosZ \
                   + "," + step + "," + RotZ + "," + latencyUDP

            ############# Math time ###################
            x_ref = (0.0001,)
            y_ref = (0.0001,)
            x_meas = PosX
            y_meas = PosY
            yaw_meas = RotZ

            # Position error
            x_error = x_ref[0] - x_meas[0]
            y_error = y_ref[0] - y_meas[0]
            dist_error = sqrt(pow(x_error, 2) + pow(y_error, 2))

            # Angle error
            angle_to_target = atan(x_error / y_error) * (180 / pi)
            angle_error_rad = angle_to_target - yaw_meas[0]
            angle_error = -angle_error_rad

            ################# Controller time #################
            kp_yaw = 2 #6.99
            kp_y = 0.1 #1.3677

            cs_yaw = kp_yaw * angle_error
            cs_y = kp_y * dist_error

            ################ Console printing ################
            #if k == 50:
             #   print("-------------- PacketNo: ", i, "--------------")
             #   print("Distance to target ", dist_error, "m")
             #   print("Controlsignal dist", cs_y, "m/s")
             #   print("Angle to target ", angle_error, "deg")
             #   print("Controlsignal yaw", cs_yaw, "deg/s")
             #   k = 0
             #   time.sleep(1)

            #k += 1
            mc._set_vel_setpoint(0, cs_y, 0, cs_yaw)
        file.close()
