from __future__ import print_function
import os
import argparse
import sys
import socket
import time
import bosdyn.client
import bosdyn.client.lease
import bosdyn.client.util
import bosdyn.geometry

import logging

from bosdyn.client import create_standard_sdk, \
    RpcError, \
    lease, \
    estop, \
    robot_command, \
    robot_state, \
    power, \
    image, \
    InvalidRequestError, \
    frame_helpers, \
    math_helpers

from bosdyn.client.robot_command import NoTimeSyncError, NotPoweredOnError, RobotCommandBuilder, RobotCommandClient, blocking_stand

from bosdyn.client.robot_command import RobotCommandBuilder, RobotCommandClient
from bosdyn.client.robot_state import RobotStateClient

from SpotUtil import *
from CreateSpot import Robot

def main(argv):

    Spot = Robot(argv)
    position = [0,0,0] 
    try:
        with Spot.keepLeaseAlive():
            Spot.wake()

            print('server started')

            # ---- USE THIS BLOCK IF CONNECTING TO A DOCKER CONTAINER -------------
            # HOST = ""  # Standard loopback interface address (localhost)        |
            # PORT = 65432  # Port to listen on (non-privileged ports are > 1023) |
            # ---------------------------------------------------------------------

            # ---- USE THIS BLOCK IF CONNECTING TO CONTAINERLESS CLIENT -------------
            HOST = '172.17.0.2'  # Docker container IP address                      |
            PORT = 80  # TCP port to open to allow for communication from localhost |
            # -----------------------------------------------------------------------

            print(f'host: {HOST}')

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((HOST, PORT))
                s.listen()
                conn, addr = s.accept()
                with conn:
                    print(f"Connected by {addr}")
                    while True:
                        data = conn.recv(1024)
                        if not data:
                            break

                        print(str(data))
                        datastr = data.decode('utf-8')

                        data_arr = datastr.split()
                        if data_arr[0] == 'stand':
                            print('stand')
                            Spot.stand(float(data_arr[1]))
                        elif data_arr[0] == 'sit':
                            print('sit')
                            Spot.sit()
                        elif data_arr[0] == "move":
                            print('move')
                            direction = Direction.FORWARDS
                            if data_arr[2].lower() == "backwards":
                                direction = Direction.BACKWARDS

                            Spot.walk(float(data_arr[1]), direction, float(data_arr[3]))
                        elif data_arr[0] == "turn":
                            print('turn')
                            rotation_direction = RotationDirection.CLOCKWISE
                            if data_arr[2].lower() == "l":
                                rotation_direction = RotationDirection.COUNTERCLOCKWISE

                            Spot.rotate(float(data_arr[1]), rotation_direction, float(data_arr[3]))

                        elif data_arr[0] == "headtilt":
                            print('head tilt')
                            Spot.head_up(float(data_arr[1]), float(data_arr[2]))

                        elif data_arr[0] == "gmove":
                            print('global point movement')
                            num_points = int(data_arr[1])
                            point_queue = []

                            for n in range(num_points):
                                point_queue.append([float(data_arr[3*n+2]), float(data_arr[3*n+3]), float(data_arr[3*n+4])])

                            x, y, w = Spot.global_point_movement(point_queue)  
                            position[0] += x; position[1] +=y; position[0] += w

                        elif data_arr[0] == "image":
                            data = Spot.captureImage()

                        conn.sendall(data)

            Spot.sleep()
            
    finally:
        print('server closed')
        Spot.getLease()


if __name__ == '__main__':
    if not main(sys.argv[1:]):
        sys.exit(1)