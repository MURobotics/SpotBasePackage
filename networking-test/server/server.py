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
from SpotMovements import *

HOST = ""  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

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

            data_arr = data.split()
            if data_arr[0] == "stand":
                stand(data_arr[1])
            elif data_arr[0] == "move":
                direction = Direction.FORWARDS
                if data_arr[2].lower() == "backwards":
                    direction = Direction.BACKWARDS

                walk(data_arr[1], direction, data_arr[3])
            elif data_arr[0] == "turn":
                rotation_direction = RotationDirection.CLOCKWISE
                if data_arr[2].lower() == "counterclockwise":
                    rotation_direction = RotationDirection.COUNTERCLOCKWISE

                rotate(data_arr[1], rotation_direction, data_arr[3])

            conn.sendall(data)