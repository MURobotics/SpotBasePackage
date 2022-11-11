from __future__ import print_function
import argparse
import sys
import time
import os
import bosdyn.client
import bosdyn.client.lease
import bosdyn.client.util
import bosdyn.geometry

from bosdyn.client.image import ImageClient
from bosdyn.client.robot_command import RobotCommandBuilder, RobotCommandClient, blocking_stand

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

    def getLease(self):
        return self.lease_client.return_lease(self.lease)

    def getLeaseClient(self):
        return self.lease_client

    def keepLeaseAlive(self):
        return bosdyn.client.lease.LeaseKeepAlive(self.lease_client)

        

    #   -----   Movement Commands   -----

    # stand() causes the robot to stand at a given height
    # height is in meters
    def stand(self, height, delay=3):
        cmd = RobotCommandBuilder.synchro_stand_command(body_height=height)
        self.command_client.robot_command(cmd)
        time.sleep(delay)