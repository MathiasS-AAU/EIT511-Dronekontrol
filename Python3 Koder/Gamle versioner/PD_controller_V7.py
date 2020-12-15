from math import *
import pandas as pd
import socket
import struct
import select
import logging
import time
import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.positioning.motion_commander import MotionCommander

# Configuration
seq = [(0.75,), (0.75,),    # Point 1
       (0.75,), (-0.75,),   # Point 2
       (-0.75,), (-0.75,),  # Point 3
       (-0.75,), (0.75,)]   # Point 4 .. more can be added
kp_yaw = 1.2445146 #3.236 # Controlfactor yaw
kd_yaw = 0.4
kp_y = 0.143 #0.143  # Controlfactor y
kd_y = 0.4
maxVel = 0.6 # Max forward velocity
maxRot = 100 # Max yawrate
refTime = 300 # Time to spend in each point [ms]
refDist = 0.25 # Distance to point [m]
prev_angle_error = 0
prev_dist_error = 0

# Constants (No need to change)
x_ref = seq[0]
y_ref = seq[1]
lastTime = int(time.time()*1000)
k = 0
i = 2
LT = int(time.time()*1000)
h = 50

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

#Errors for error function
def error(x_r, y_r):
    ############# SDK time ###################)
    empty_socket()
    data, addr = sock_in.recvfrom(1024)
    ST = int(time.time() * 1000)  # package recieved now
    res = ''.join(format(x, '02x') for x in data)

    x_meas = struct.unpack_from('d', data, 0)  # TX
    y_meas = struct.unpack_from('d', data, 8)  # TY
    # z_meas = struct.unpack_from('d', data, 16) # TZ

    # pitch_meas = struct.unpack_from('d', data, 24) # RX
    # roll_meas = struct.unpack_from('d', data, 32) # RY
    yaw_meas = struct.unpack_from('d', data, 40)  # RZ

    ############# Math time ###################
    # Distance error
    x_error = x_r - x_meas[0]
    y_error = y_r - y_meas[0]
    dist_err = sqrt(pow(y_error, 2) + pow(x_error, 2))

    # Angle error
    if 0 <= y_error:
        angle_of_target = -atan(x_error / y_error) * (180 / pi)
    elif 0 < x_error: # 0 > Y_error would always be true anyway
        angle_of_target = (-atan(x_error / y_error) * (180 / pi)) - 180
    elif 0 > x_error: # 0 > Y_error would always be true anyway
        angle_of_target = (-atan(x_error / y_error) * (180 / pi)) + 180

    angle_err = yaw_meas[0] - angle_of_target

    if -180 > angle_err:
        angle_err = angle_err + 360
    elif 180 < angle_err:
        angle_err = angle_err - 360
    return angle_err, dist_err

def empty_socket():
    while 1:
        inputready, o, e = select.select([sock_in],[sock_in],[sock_in], 0.0)
        if len(inputready)==0: break
        for s in inputready: s.recv(1024)

def DebugPrint():
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

############# Start flight ###################
with SyncCrazyflie(URI, cf=Crazyflie(rw_cache='./cache')) as scf:
    print("Crazyflie taking off")
    with MotionCommander(scf) as mc:
        #cf.param.set_value('kalman.resetEstimation', '1')
        #time.sleep(0.1)
        #cf.param.set_value('kalman.resetEstimation', '0')
        #time.sleep(2)
        print("Starting control sequence!")
        while True:
            if int(time.time()*1000) - LT >= h:

                errors = error(x_ref[0], y_ref[0])
                angle_error = errors[0]
                dist_error = errors[1]

                ################# Controller time #################
                # Control signal calculation
                if x_meas == 0 and y_meas == 0:
                    cs_y = 0
                    cs_yaw = 0
                elif dist_error <= refDist/2:
                    cs_yaw = kp_yaw*(angle_error+kd_yaw*((angle_error-prev_angle_error)/h))
                    cs_y = 0
                else :
                    cs_yaw = kp_yaw*(angle_error+kd_yaw*((angle_error-prev_angle_error)/h))
                    cs_y = kp_y*(dist_error+kd_y*((dist_error-prev_dist_error)/h))

                prev_dist_error = dist_error
                prev_angle_error = angle_error

                # Velocity limitation
                if cs_yaw > maxRot and cs_y > maxVel:
                    cs_yaw = maxRot
                    cs_y = maxVel
                elif cs_yaw > maxRot:
                    cs_yaw = maxRot
                elif cs_y > maxVel:
                    cs_y = maxVel

                mc._set_vel_setpoint(cs_y, 0, 0, cs_yaw)
                delay = int(time.time() * 1000) - ST #package has been used now
                print(delay)

                ############# Sequence reference ###################
                if dist_error <= refDist:
                    if (int(time.time()*1000)-lastTime) >= refTime:
                        if i >= len(seq):
                            print("Done with point", int(i/2), "- sequence done! :-)")
                            break
                        elif i == len(seq)-2:
                            refTime = int(refTime/2)
                        x_ref = seq[i]
                        y_ref = seq[i+1]
                        print("Done with point", int(i/2))
                        i += 2
                        lastTime = int(time.time()*1000)
                else :
                    lastTime = int(time.time()*1000)

                #DebugPrint()
                LT = int(time.time()*1000)
