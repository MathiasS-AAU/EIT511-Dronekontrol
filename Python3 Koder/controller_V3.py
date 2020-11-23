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

def DebugPrint:
    if k >= 50:
        print("--- Packet:", i, "--------- Latency:", latencyUDP, "---")
        print("Distance to target =", dist_error, "m")
        print("Measured position  =", x_meas, ":", y_meas, "m")
        print("Controlsignal dist =", cs_y, "m/s")
        print("Angle to target    =", angle_error, "deg")
        print("Measured yaw       =", yaw_meas, "deg")
        print("Controlsignal yaw  =", cs_yaw, "deg/s")
        k = -1    
    k += 1

# Define sequence
x1_ref = (1,)
y1_ref = (1,)
x2_ref = (1,)
y2_ref = (-1,)
x3_ref = (-1,)
y3_ref = (-1,)
x4_ref = (-1,)
y4_ref = (1,)

# Constants
seq = [(x1_ref), (y1_ref), (x2_ref), (y2_ref), (x3_ref), (y3_ref), (x4_ref), (y4_ref)]
x_ref = (0.001,)
y_ref = (0.001,)
kp_yaw = 3.236
kp_y = 0.143
maxLat = 460 # Max latency
maxVel = 2 # Max forward velocity
maxRot = 50 # Max yawrate
k = 0
refTime = 1000 # [ms]

# DataStream Setup
UDP_IP_in = "172.26.56.152" # Linuxterminal: Hostname -I
UDP_PORT_in = 5004
sock_in = socket.socket(socket.AF_INET,
                        socket.SOCK_DGRAM)
sock_in.bind((UDP_IP_in, UDP_PORT_in))

# Crazyflie Setup
URI = 'radio://0/80/250K'
logging.basicConfig(level=logging.ERROR)
cflib.crtp.init_drivers(enable_debug_driver=False)

############# Start flight ###################
x_ref = seq[0]
y_ref = seq[1]
i = 2
with SyncCrazyflie(URI, cf=Crazyflie(rw_cache='./cache')) as scf:
    print("Crazyflie taking off")
    with MotionCommander(scf) as mc:
        time.sleep(1)
        mc._reset_position_estimator
        time.sleep(0.1)
        print("Starting control sequence!")
        while True:
            while True: # Only use 'fresh' packages
                data, addr = sock_in.recvfrom(1024)
                i = struct.unpack_from('Q', data, 48)
                timespend = int(time.time()*1000)
                latencyUDP = timespend - i[0]
                if latencyUDP <= maxLat:
                    break
                #print("--- Packet:", i, "dumped! Latency:", latencyUDP, ">", maxLat, "ms")
            res = ''.join(format(x, '02x') for x in data)

            # Read values from packet
            x_meas = struct.unpack_from('d', data, 0) # TX
            y_meas = struct.unpack_from('d', data, 8) # TY
            z_meas = struct.unpack_from('d', data, 16) # TZ
            pitch_meas = struct.unpack_from('d', data, 24) # RX
            roll_meas = struct.unpack_from('d', data, 32) # RY
            yaw_meas = struct.unpack_from('d', data, 40) # RZ

            ############# Math time ###################
            # Distance error
            x_error = x_ref[0] - x_meas[0]
            y_error = y_ref[0] - y_meas[0]
            dist_error = sqrt(pow(y_error, 2) + pow(x_error, 2))

            # Angle error
            if 0 <= y_error:
                angle_of_target = -atan(x_error / y_error) * (180 / pi)
            elif 0 > y_error and 0 < x_error:
                angle_of_target = (-atan(x_error / y_error) * (180 / pi)) - 180
            elif 0 > y_error and 0 > x_error:
                angle_of_target = (-atan(x_error / y_error) * (180 / pi)) + 180
            angle_error = yaw_meas[0] - angle_of_target
            if -180 > angle_error:
                angle_error = angle_error + 360
            elif 180 < angle_error:
                angle_error = angle_error - 360

            ############# Sequence reference ###################
            if dist_error <= 0.25:
                timeInRef2 = int(time.time()*1000)
                if (timeInRef2-timeInRef1) >= refTime:
                    x_ref = seq[i]
                    i += 1
                    y_ref = seq[i]
                    i += 1
                    print("Referencepoint met! Next pont is", x_ref, ",", y_ref)
                    if i >= len(seq):
                        print("Sequence done!")
                        break

            ################# Controller time #################
            if x_meas == 0 and y_meas == 0:
                cs_y = 0
                cs_yaw = 0
            else :
                cs_yaw = kp_yaw * angle_error
                cs_y = kp_y * dist_error

            # Velocity limitation
            if cs_yaw > maxRot and cs_y > maxVel:
                cs_yaw = maxRot
                cs_y = maxVel
            elif cs_yaw > maxRot:
                cs_yaw = maxRot
            elif cs_y > maxVel:
                cs_y = maxVel

            mc._set_vel_setpoint(cs_y, 0, 0, cs_yaw)

            #DebugPrint()
            #print(angle_of_target)
