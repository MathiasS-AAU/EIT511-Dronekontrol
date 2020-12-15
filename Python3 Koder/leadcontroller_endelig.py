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
#seq = [(-0.75,), (0.75,),
#       (0.75,), (0.75,),    # Point 1
#       (0.75,), (-0.75,),   # Point 2
#       (-0.75,), (-0.75,)]  # Point 3
          # Point 4 .. more can be added
seq = [(0.5,), (0.5,),
       (0.5,),(-0.5,),
       (-0.5,),(-0.5,),# Point 1
       (-0.5,), (0.5,)]  # Point 3
          # Point 4 .. more can be added
k = 1.2274 #Propertionalcontrol, translation
a = 0.561 # Nulpunkt i lead controller
b = 1.69 # Pol i lead controller

kp_yaw = 1.7947 # Controlfactor yaw 
maxVel = 1 #0.85#0.6 # Max forward velocity
maxRot = 300 # Max yawrate
refTime = 500 # Time to spend in each point [ms]
refDist = 0.2 # Distance to point [m]
prev_angle_error = 0
prev_y_error = 0
prev_x_error = 0
prev_cs_y = 0
prev_d_y = 0
prev_d_x = 0
prev_cs_x = 0

cs_y = 0
cs_x = 0
cs_yaw = 0
dist_error = 0
angle_error = 0


# Constants (No need to change)
x_ref = seq[0]
y_ref = seq[1]
lastTime = int(time.time()*1000)
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
                    dist_error = 0
                    angle_error = 0
                    print("alt er lort")

                else :
                    cs_yaw = kp_yaw * angle_error # Yaw P

                    ## X controller ##
                    cs_x = ((b*0.05+2)*(x_error-prev_x_error)-prev_cs_x*(k*a*0.05+k*2))/(k*a*0.05+k*2)
                    prev_x_error = x_error
                    prev_cs_x = cs_x
                    
                    ## Y controller ##
                    cs_y = ((b*0.05+2)*(y_error-prev_y_error)-prev_cs_y*(k*a*0.05+k*2))/(k*a*0.05+k*2)
                    prev_y_error = y_error
                    prev_cs_y = cs_y
                    #print("cs_x,cs_y:",(cs_x,cs_y))
                    
                #print("cs_y",cs_y, "disttotarget", dist_error, "prev", prev_dist_error)
                
                # Velocity limitation
                if (abs(cs_yaw) > maxRot and abs(cs_y) > maxVel):
                    cs_yaw = copysign(maxRot,cs_yaw)
                    cs_y = cs_y * maxVel
                elif abs(cs_yaw) > maxRot:
                    cs_yaw = copysign(maxRot,cs_yaw)
                elif abs(cs_y) > maxVel:
                    cs_y = cs_y * maxVel
                    
                if (abs(cs_yaw) > maxRot and abs(cs_x) > maxVel):
                    cs_yaw = copysign(maxRot,cs_yaw)
                    cs_x = cs_x * maxVel
                elif abs(cs_yaw) > maxRot:
                    cs_yaw = copysign(maxRot,cs_yaw)
                elif abs(cs_x) > maxVel:
                    cs_x = cs_x * maxVel

                prev_y_error = y_error
                prev_cs_y = cs_y
                prev_x_error = x_error
                prev_cs_x = cs_x

                print("cs_x,cs_y:",(cs_x,cs_y))
                mc._set_vel_setpoint(cs_y, -cs_x, 0, cs_yaw)

                ############# Sequence reference ###################
                if dist_error <= refDist and dist_error != 0:
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
                        prev_y_error = 0
                        prev_cs_y = 0
                        prev_x_error = 0
                        prev_cs_x = 0
                else :
                    lastTime = int(time.time()*1000)

                #DebugPrint()
                LT = int(time.time()*1000)
