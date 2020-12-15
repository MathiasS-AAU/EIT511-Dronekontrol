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
kp_yaw = 3.236 # 1.2445146  Controlfactor yaw
#kd_yaw = 0.4
maxVel = 0.2 #0.85#0.6 # Max forward velocity
maxRot = 300 # Max yawrate
refTime = 300 # Time to spend in each point [ms]
refDist = 0.2 # Distance to point [m]

kp = 0.6 #0.455 #0.6508 #0.3495 #0.1726 #0.143  # Controlfactor y
ki = 0 #0.03 #0.04746
kd = 0.53 #0.348 #0.3937*10 #0.276 #0.1486 #

int_lim = 0.1

prev_i_y = 0
prev_y_error = 0
prev_y_meas = 0
prev_d_y = 0

prev_i_x = 0
prev_x_error = 0
prev_x_meas = 0
prev_d_x = 0

# Constants (No need to change)
x_ref = seq[0]
y_ref = seq[1]
lastTime = int(time.time()*1000)
k = 0
i = 2
LT = int(time.time()*1000)
h = 10000
t = 0.05 # 1

# DataStream Setup
UDP_IP_in = "192.168.137.92" # Linuxterminal: Hostname -I
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
                    angle_error = 0
                    print("alt er lort")
                    
                else :
                    cs_yaw = kp_yaw * angle_error # Yaw P

                 ##### Y retning ########
                    ## Propertional
                    p_y = kp * y_error

                    ## Integrator
                    i_y = prev_i_y + ((0.5 * ki * h) * (y_error + prev_y_error))

                        ## Anti wind-up
                    if i_y > int_lim:
                        i_y = int_lim
                    elif i_y < -int_lim:
                        i_y = -int_lim
                    i_y = 0
                    ## Differentiator
                    d_y = (2 * kd * (y_meas[0]-prev_y_meas) + (2 * t - h) * prev_d_y) /(2 * t + h)
                    #d_y = ((2 * kd)/h * y_meas[0]-prev_y_meas) + prev_d_y

                    ## Control signal
                    cs_y = p_y + i_y + d_y

                    # Update old values
                    prev_i_y = i_y
                    prev_d_y = d_y
                    prev_y_error = y_error
                    prev_y_meas = y_meas[0]

                 ##### X retning ########
                    ## Propertional
                    p_x = kp * x_error

                    ## Integrator
                    i_x = prev_i_x + ((0.5 * ki * h) * (x_error + prev_x_error))

                        ## Anti wind-up
                    if i_x > int_lim:
                        i_x = int_lim
                    elif i_x < -int_lim:
                        i_x = -int_lim
                    i_x = 0
                    ## Differentiator
                    d_x = (2 * kd * (x_meas[0]-prev_x_meas) + (2 * t - h) * prev_d_x) /(2 * t + h)
                    #d_x = ((2 * kd)/h * x_meas[0]-prev_x_meas) + prev_d_x
                    
                    ## Control signal
                    cs_x = p_x + i_x + d_x

                    # Update old values
                    prev_i_x = i_x
                    prev_d_x = d_x
                    prev_x_error = x_error
                    prev_x_meas = x_meas[0]


                print(cs_x, cs_y)
                
                # Velocity limitation
                if (abs(cs_yaw) > maxRot and abs(cs_y) > maxVel):
                    cs_yaw = copysign(maxRot,cs_yaw)
                    cs_y = copysign(maxVel,cs_y)
                elif abs(cs_yaw) > maxRot:
                    cs_yaw = copysign(maxRot,cs_yaw)
                elif abs(cs_y) > maxVel:
                    cs_y = copysign(maxVel,cs_y)
                    
                if (abs(cs_yaw) > maxRot and abs(cs_x) > maxVel):
                    cs_yaw = copysign(maxRot,cs_yaw)
                    cs_x = copysign(maxVel,cs_x)
                elif abs(cs_yaw) > maxRot:
                    cs_yaw = copysign(maxRot,cs_yaw)
                elif abs(cs_x) > maxVel:
                    cs_x = copysign(maxVel,cs_x)
                    
                print("L")
                mc._set_vel_setpoint(0, 0, -100, 0)
                ############# Sequence reference ###################
                if dist_error <= refDist and dist_error != 0:
                    if (int(time.time()*1000)-lastTime) >= refTime:
                        if i >= len(seq):
                            print("Done with point", int(i/2), "- sequence done! :-)")
                            prev_i_y = 0
                            prev_y_error = 0
                            prev_y_meas = 0
                            prev_d_y = 0
                            prev_i_x = 0
                            prev_x_error = 0
                            prev_x_meas = 0
                            prev_d_x = 0
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
