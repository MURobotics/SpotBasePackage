from __future__ import print_function
import argparse
import sys
import time
import os
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
    InvalidRequestError

from bosdyn.client.robot_command import NoTimeSyncError, NotPoweredOnError, RobotCommandBuilder, RobotCommandClient, blocking_stand

import spotutil as util
from spotutil import Direction

class SpotMovement:
    def __init__(self, robot_client):
        self.robot_client = robot_client

    def execute_command(self, cmd, time=None):
        print("Running Command")
        try:
            self.robot_client.robot_command(cmd, time)
        except RpcError:
            logging.error("Problem communicating with the Spot")
        except InvalidRequestError:
            logging.error("Invalid request")
        except NoTimeSyncError:
            logging.error("It's been too long since last time-sync")
        except NotPoweredOnError:
            logging.error("Engines are not powered")

    def move_velocity(self, v_x=0.0, v_y=0.0, v_rot=0.0, duration=0.0):
        print(f"velocity {v_y}")
        self.execute_command(
            RobotCommandBuilder.synchro_velocity_command(
                v_x=v_x,
                v_y=v_y,
                v_rot=v_rot
            ),
            util.get_command_duration(duration)
        )
    
    #heading in radians, postion relative to robot frame
    def move_position(self, x_pos=0.0, y_pos=0.0, heading=0.0, duration=0.0):
        self.execute_command(
            RobotCommandBuilder.synchro_trajectory_command_in_body_frame(
                goal_x_rt_body = x_pos, 
                goal_y_rt_body = y_pos, 
                goal_heading_rt_body = heading
            ),
            util.get_command_duration(duration)
        )

    def strafe(self, speed: float, direction: Direction, duration=0.0):
        if not (direction is Direction.LEFT or direction is Direction.RIGHT):
            print("No strafing?")
            raise Exception("Invalid direction for strafing")

        speed = speed if direction is Direction.LEFT else -speed
        self.move_velocity(0, speed, 0, duration)

    def walk(self, speed: float, direction: Direction, duration=0.0):
        if not (direction is Direction.FORWARDS or direction is Direction.BACKWARDS):
            print("No walking?")
            raise Exception("Invalid direction for walking")

        speed = speed if direction is Direction.FORWARDS else -speed
        self.move_velocity(speed, 0, 0, duration)

    
    
