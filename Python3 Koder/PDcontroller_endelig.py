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
seq = [(-0.5,), (0,),   # Point 1
       (-0.5,), (-0.5,),# Point 2
       (0,), (-0.5,),   # Point 3
       (0.5,),(-0.5,),  # Point 4
       (0.5,),(0,),     # Point 5
       (0.5,),(0.5,),   # Point 6
       (0,),(0.5,),     # Point 7
       (-0.5,), (0.5,)] # Point 8
kp_yaw = 1.7947
kp = 0.7039
kd = 0.4117 
maxVel = 0.4 # Controlfactoring
maxRot = 300 # Max yaw anglevelocity
refTime = 400 # Time to spend in each point [ms]
refDist = 0.15 # Distance to point [m]

# Constants
x_ref = seq[0]
y_ref = seq[1]
lastTime = int(time.time()*1000)
LT = int(time.time()*1000)
i = 2
h = 50
prev_angle_error = 0
prev_y_error = 0
prev_x_error = 0
prev_cs_y = 0
prev_d_y = 0
prev_d_x = 0
prev_cs_x = 0
abe = 0

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

def empty_socket():
    while 1:
        inputready, o, e = select.select([sock_in],[sock_in],[sock_in], 0.0)
        if len(inputready)==0: break
        for s in inputready: s.recv(1024)

############# Start flight ###################
with SyncCrazyflie(URI, cf=Crazyflie(rw_cache='./cache')) as scf:
    print("Crazyflie taking off")
    with MotionCommander(scf) as mc:
        print("Starting control sequence!")
        while True:
            if int(time.time()*1000) - LT >= h:
                LT = int(time.time()*1000)
                ############# SDK time ###################)
                empty_socket()
                data, addr = sock_in.recvfrom(1024)
                res = ''.join(format(x, '02x') for x in data)

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
                angle_error = yaw_meas[0] #angle_of_target
                
                ################# Controller time #################
                # Control signal calculation
                if x_meas[0] == 0 and y_meas[0] == 0:
                    cs_y = 0
                    cs_x = 0
                    cs_yaw = 0
                    dist_error = 0
                    angle_error = 0
                    print("Vicon can't see the drone!")
                else :
                    # Yaw controller
                    cs_yaw = kp_yaw * angle_error
                    # X controller
                    cs_x = (x_error * 2 * kd - 2 * prev_x_error * kd)/0.05 + kp * (x_error + prev_x_error) - prev_cs_x
                    prev_x_error = x_error
                    prev_cs_x = cs_x
                    # Y controller
                    cs_y = (y_error * 2 * kd - 2 * prev_y_error * kd)/0.05 + kp * (y_error + prev_y_error) - prev_cs_y
                    prev_y_error = y_error
                    prev_cs_y = cs_y
   
                # Velocity limitation
                cs_y = cs_y * maxVel
                cs_x = cs_x * maxVel

                prev_y_error = y_error
                prev_cs_y = cs_y
                prev_x_error = x_error
                prev_cs_x = cs_x

                print("cs_x,cs_y:",(cs_x,cs_y))
                mc._set_vel_setpoint(cs_y, -cs_x, 0, cs_yaw)
                if i >= len(seq) and dist_error <= refDist and dist_error != 0:
                    cs_y = 0
                    cs_x = 0
                    mc._set_vel_setpoint(cs_y, -cs_x, -0.1, cs_yaw)
                    print("Done with point", int(i/2), "- sequence done! :-)")

                ############# Sequence reference ###################
                if dist_error <= refDist and dist_error != 0:
                    if (int(time.time()*1000)-lastTime) >= refTime:
                        if i >= len(seq):
                            cs_y = 0
                            cs_x = 0
                            mc._set_vel_setpoint(cs_y, -cs_x, 0, cs_yaw)
                            print("Done with point", int(i/2), "- sequence done! :-)")
                        elif i == len(seq)-2 and abe==0:
                            refDist = 0.13
                            refTime = 1000
                            abe = 1
                        x_ref = seq[i]
                        y_ref = seq[i+1]
                        print("Done with point", int(i/2))
                        if i < len(seq)-1:
                            i += 2
                        lastTime = int(time.time()*1000)
                        prev_y_error = 0
                        prev_cs_y = 0
                        prev_x_error = 0
                        prev_cs_x = 0
                else :
                    lastTime = int(time.time()*1000)
