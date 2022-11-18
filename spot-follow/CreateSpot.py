from __future__ import print_function
import argparse
import sys
import time
import os
import bosdyn.client
import bosdyn.client.lease
import bosdyn.client.util
import bosdyn.geometry
import spotutil as util

from bosdyn.client.image import ImageClient
from bosdyn.client.robot_command import RobotCommandBuilder, RobotCommandClient, blocking_stand

#   [docker-compose build] while connected to wifi to compile
#   [docker-compose up] while connected to spot to run

class Robot:
    #   -----   Startup commands    -----

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
        self.default_delay = 3
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

    def getLease(self):
        return self.lease_client.return_lease(self.lease)

    def getLeaseClient(self):
        return self.lease_client

    def keepLeaseAlive(self):
        return bosdyn.client.lease.LeaseKeepAlive(self.lease_client)

    def setDefaultDelay(self, delay):
        self.default_delay = delay


    #   -----   Movement Commands   -----

    def command(self, cmd, delay=None, duration=None):
        self.command_client.robot_command(cmd, duration)
        self.delay(delay);

    # delay() is delay between commands. Defaults to default_delay value [set with setDefaultDelay(). default is 3]
    def delay(self, delay=None):
        if (delay is None): 
            delay = self.default_delay
        time.sleep(delay)

    # stand() causes the robot to stand at a given height
    # height is in meters
    def stand(self, height, delay=None):
        self.command(
            RobotCommandBuilder.synchro_stand_command(body_height=height),
            delay    
        )

    def sit(self, delay=None):
        self.command(
            RobotCommandBuilder.synchro_sit_command(),
            delay
        )
    # pose_body() twists the robot's torso without moving the legs
    # yaw, roll, and pitch are measured in radians
    def pose_body(self, yaw=0.0, roll=0.0, pitch=0.0, delay=None):
        self.command(
            RobotCommandBuilder.synchro_stand_command(
                footprint_R_body = bosdyn.geometry.EulerZXY(yaw=yaw, roll=roll, pitch=pitch)
            ),
            delay
        )

    # x and y are in meters relative to Spot (x is forward)
    def trajectory(self, x=0.0, y=0.0, heading=0.0, delay=None, duration=0):
        self.command(
            RobotCommandBuilder().synchro_trajectory_command_in_body_frame(x, y, heading, self.robot.get_frame_tree_snapshot()),
            delay,
            util.get_command_duration(duration)
        )




