from __future__ import print_function
import argparse
import sys
# import time
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

    def __init__(self, command_client, time):
        self.command_client = command_client
        self.time = time


    def stand(self, height):
        cmd = RobotCommandBuilder.synchro_stand_command(body_height=height)
        self.command_client.robot_command(cmd)
        # robot.logger.info("Robot standing tall.")
        self.time.sleep(3)
