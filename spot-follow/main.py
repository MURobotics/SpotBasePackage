# Copyright (c) 2021 Boston Dynamics, Inc.  All rights reserved.
#
# Downloading, reproducing, distributing or otherwise using the SDK Software
# is subject to the terms and conditions of the Boston Dynamics Software
# Development Kit License (20191101-BDSDK-SL).

"""Tutorial to show how to use the Boston Dynamics API"""
from __future__ import print_function
import os
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

import sys
from CreateSpot import Robot
from bosdyn.client.frame_helpers import BODY_FRAME_NAME, ODOM_FRAME_NAME, VISION_FRAME_NAME
from CupidShuffle import dance
from SpotUtil import Camera

def main(argv):
    Spot = Robot(argv)
    
    # Taking multiple pictures

    counter = 0
    while True:
        print(f"Counter = {counter}")
        Spot.saveImage(Camera.FRONTLEFT, name=f"spot_img_{counter}.jpg")
        counter += 1
        time.sleep(0.7)
    
    print("Stopping")

if __name__ == '__main__':
    if not main(sys.argv[1:]):
        sys.exit(1)