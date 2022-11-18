from __future__ import print_function
import argparse
import sys
import time
import os
import bosdyn.client
import bosdyn.client.lease
import bosdyn.client.util
import bosdyn.geometry
from bosdyn.geometry import EulerZXY

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

from bosdyn.client.image import ImageClient
from bosdyn.client.robot_command import RobotCommandBuilder, RobotCommandClient, blocking_stand

from SpotUtil import Direction, RotationDirection, get_command_duration, pause

#   [docker-compose build] while connected to wifi to compile
#   [docker-compose up] while connected to spot to run

class Robot:
    # init() initializes starting values and uses the run() function to connect to spot
    def __init__(self, argv):
        parser = argparse.ArgumentParser()
        bosdyn.client.util.add_common_arguments(parser)
        parser.add_argument('-s', '--save', action='store_true', help='Save the image captured by Spot to the working directory. To chose the save location, use --save_path instead.')
        parser.add_argument('--save-path', default=None, nargs='?', help='Save the image captured by Spot to the provided directory. Invalid path saves to working directory.')
        options = parser.parse_args(argv)
        try:
            self.run(options)
        except Exception as exc:
            self.err("Hello, Spot threw an exception: %r", exc)


    # run() connects to the spot robot and sets up time sync
    # If there are issues connecting, ensure the spot_account.env file in the secrets folder is properly formatted with correct credentials
    # run() is run automatically upon initializing the Robot class
    def run(self, config):
        bosdyn.client.util.setup_logging(config.verbose)  
        self.sdk = bosdyn.client.create_standard_sdk('HelloSpotClient')
        self.robot = self.sdk.create_robot(config.hostname)
        self.robot.authenticate(config.username, config.password)
        self.robot.time_sync.wait_for_sync()
        assert not self.robot.is_estopped(), "Robot is estopped. Please use an external E-Stop client, " \
                                        "such as the estop SDK example, to configure E-Stop."  
        self.lease_client = self.robot.ensure_client(bosdyn.client.lease.LeaseClient.default_service_name)
        self.lease = self.lease_client.acquire()

    # wake() powers on the robot and causes it to stand
    # wake() must be run before any other commands
    def wake(self):
        self.log("Powering on robot... This may take several seconds.")
        self.robot.power_on(timeout_sec=20)
        assert self.robot.is_powered_on(), "Robot power on failed."
        self.log("Robot powered on.")
        self.log("Commanding robot to stand...")
        self.command_client = self.robot.ensure_client(RobotCommandClient.default_service_name)
        blocking_stand(self.command_client, timeout_sec=10)
        self.log("Robot standing.")
        time.sleep(3)

    # sleep() causes the robot to power off.
    # run sleep() at the end of every program
    def sleep(self):
            self.robot.power_off(cut_immediately=False, timeout_sec=20)
            assert not self.robot.is_powered_on(), "Robot power off failed."
            self.log("Robot safely powered off.")

    def log(self, info):#, *args="", log_type=0):
        self.robot.logger.info(info)
        # if (log_type == 0):
        #     self.robot.logger.info(info, args)
        # elif (log_type = 1):
        #     self.robot.logger.error(info, args)

    def err(self, info, *args):
        self.robot.logger.error(info, args)

    def getCommandClient(self):
        return self.command_client

    def getLease(self):
        return self.lease_client.return_lease(self.lease)

    def getLeaseClient(self):
        return self.lease_client

    def keepLeaseAlive(self):
        return bosdyn.client.lease.LeaseKeepAlive(self.lease_client)

        

    #   -----   Movement Commands   -----

    #This functions runs all commands
    def execute_command(self, cmd, time=None):
        print("Running Command")
        try:
            print(cmd)
            self.robot.getCommandClient().robot_command(cmd, time)
        except RpcError:
            logging.error("Problem communicating with the Spot")
        except InvalidRequestError:
            logging.error("Invalid request")
        except NoTimeSyncError:
            logging.error("It's been too long since last time-sync")
        except NotPoweredOnError:
            logging.error("Engines are not powered")
        
        pause(3)

    # stand() causes the robot to stand at a given height
    # height is in meters
    def stand(self, height = 0.0) -> None:
        self.execute_command(
            RobotCommandBuilder.synchro_stand_command(body_height=height)
        )

    #sit() causes the robot to sit
    def sit(self) -> None:
        self.execute_command(
            RobotCommandBuilder.synchro_sit_command()
        )

    #Changes the orientation of the robot with respect to its geometric center
    #Also needs a height as it is run in the stand command
    def rotate_body(self, height = 0.0, yaw=0.0, roll=0.0, pitch=0.0) -> None:
        self.execute_command(
            RobotCommandBuilder.synchro_sit_command(
                body_height = height,
                footprint_R_body = EulerZXY(yaw=yaw, roll=roll, pitch=pitch)
            )
        )
    
    #Runs a synchro velocity command
    def move_velocity(self, v_x=0.0, v_y=0.0, v_rot=0.0, duration=0.0) -> None:
        print(f"velocity {v_y}")
        self.execute_command(
            RobotCommandBuilder.synchro_velocity_command(
                v_x=v_x,
                v_y=v_y,
                v_rot=v_rot
            ),
            get_command_duration(duration)
        )
    
    #Runs a synchro trajectory command
    #heading in radians, postion relative to robot frame
    def move_position(self, x_pos=0.0, y_pos=0.0, heading=0.0, duration=0.0) -> None:
        self.execute_command(
            RobotCommandBuilder.synchro_trajectory_command_in_body_frame(
                goal_x_rt_body = x_pos, 
                goal_y_rt_body = y_pos, 
                goal_heading_rt_body = heading
            ),
            get_command_duration(duration)
        )

    #Given an 2d array of positions in the format [x_pos, y_pos, heading, duration]
    #the robot will go through those points
    def move_on_path(self, positions : float = None):
        for position in positions:
            self.execute_command(
            RobotCommandBuilder.synchro_trajectory_command_in_body_frame(
                goal_x_rt_body = position[0], 
                goal_y_rt_body = position[1], 
                goal_heading_rt_body = position[2]
            ),
            get_command_duration(position[3])
        )


    #Moves left or right
    def strafe(self, speed: float, direction: Direction, duration=0.0) -> None:
        if (not (direction is Direction.LEFT or direction is Direction.RIGHT)):
            print("No strafing?")
            raise Exception("Invalid direction for strafing")

        speed = speed if direction is Direction.LEFT else -speed
        self.move_velocity(0, speed, 0, duration)

    #Moves forwards or backwards
    def walk(self, speed: float, direction: Direction, duration=0.0) -> None:
        if (not (direction is Direction.FORWARDS or direction is Direction.BACKWARDS)):
            print("No walking?")
            raise Exception("Invalid direction for walking")

        speed = speed if direction is Direction.FORWARDS else -speed
        self.move_velocity(speed, 0, 0, duration)

    #Rotates counterclockwise or clockwise
    def rotate(self, rot_speed: float, rot_direction: RotationDirection, duration = 0.0) -> None:
        rot_speed = rot_speed if rot_direction is RotationDirection.COUNTERCLOCKWISE else -rot_speed
        self.move_velocity(0, 0, rot_speed, duration)

    