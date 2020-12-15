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
file = open(r"/home/eit511/Desktop/test_stepY.csv", "w")
text = "Time,X,Y,Z,step,Yaw,latencyUDP\n"
step = 0

# DataStream Setup
UDP_IP_in = "169.254.79.90"
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
        #while True:
        for x in range(1,1000):
            #print("L1")
            while True:
                #print("L2")
                data, addr = sock_in.recvfrom(1024)  # buffer size is 1024 bytes
                i = struct.unpack_from('Q', data, 48)
                timespend = int(time.time()*1000)
                #print("L3")
                latencyUDP = timespend - i[0]
                if latencyUDP < 460 :
                    print(latencyUDP)
                    break
                #print("L4")
                #print(timespend - i[0])
            #print("Time send:", i[0], "Time recieved:", int(time.time()*1000), "Time spend:", (int(time.time()*1000) - i[0]))
            # print as hex
            res = ''.join(format(x, '02x') for x in data)

            # Read values from packet
            PosX = struct.unpack_from('d', data, 0)
            PosY = struct.unpack_from('d', data, 8)
            PosZ = struct.unpack_from('d', data, 16)
            RotX = struct.unpack_from('d', data, 24)
            RotY = struct.unpack_from('d', data, 32)
            RotZ = struct.unpack_from('d', data, 40)
            #print(PosX)
            #change file
            #File = open(r"/home/eit511/Desktop/test.csv",'w+')
            
            text = text + str(i[0]) + "," + str(PosX[0]) + "," + str(PosY[0]) + "," + str(PosZ[0]) \
                   + "," + str(step) + "," + str(RotZ[0]) + "," + str(latencyUDP) + "\n"
            
            

            ############# Math time ###################
            x_ref = 0.0001
            y_ref = 0.0001


            #pos_meas = pd.read_csv("C:/Users/krist/Documents/MATLAB/511_day3_xFREM.csv") #<- for debug
            #x_meas = pos_meas.TX
            #y_meas = pos_meas.TY
            #yaw_meas = pos_meas.RZ

            x_meas = PosX[0]
            y_meas = PosY[0]
            yaw_meas = RotZ[0]

            #x_meas = (-6,)
            # y_meas = (-5,)
            #yaw_meas = (-180,)


            x_error = x_ref - x_meas
            y_error = y_ref - y_meas
            dist_error = sqrt(pow(y_error, 2) + pow(x_error, 2))

            # Angle error
            if 0 <= y_error:
                angle_of_target = -atan(x_error / y_error) * (180 / pi)
            elif 0 > y_error and 0 < x_error:
                angle_of_target = (-atan(x_error / y_error) * (180 / pi)) - 180
            elif 0 > y_error and 0 > x_error:
                angle_of_target = (-atan(x_error / y_error) * (180 / pi)) + 180


            angle_error = yaw_meas - angle_of_target
            if -180 > angle_error:
                angle_error = angle_error + 360
            elif 180 < angle_error:
                angle_error = angle_error - 360

            ################# Controller time #################
            kp_yaw = 2 # 6.99
            kp_y = 3.2 # 1.3677

            #cs_yaw = kp_yaw * angle_error
            #cs_y = kp_y * dist_error

            if x_meas == 0 and y_meas == 0 :
                cs_y = 0
            #else yaw_meas == 0 :
                #cs_yaw = 0
            else :
                cs_yaw = kp_yaw * angle_error
                cs_y = kp_y * dist_error

            ################ Console printing ################
            #if k == 50:
                #print("-------------- PacketNo: ", i, "--------------")
                #print("Distance to target ", dist_error, "m")
                #print("Measured position ", x_meas, ":", y_meas, "m")
                #print("Controlsignal dist", cs_y, "m/s")
                #print("Angle to target ", angle_error, "deg")
                #print("Measured yaw ", yaw_meas, "deg")
                #print("Controlsignal yaw", cs_yaw, "deg/s")
                #k = 0
                #mc._set_vel_setpoint(cs_y, 0, 0, cs_yaw)

            #k += 1
            if x > 200:
                mc._set_vel_setpoint(0.5, 0 , 0, 0)
                step=1
                print ("step")
                if PosX[0] == 0.0:
                    break
            else:
                mc._set_vel_setpoint(0, 0, 0, cs_yaw)
        file.write(text)
        file.close()
