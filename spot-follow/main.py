# Copyright (c) 2021 Boston Dynamics, Inc.  All rights reserved.
#
# Downloading, reproducing, distributing or otherwise using the SDK Software
# is subject to the terms and conditions of the Boston Dynamics Software
# Development Kit License (20191101-BDSDK-SL).

"""Tutorial to show how to use the Boston Dynamics API"""
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

import sys
import CreateSpot
from CupidShuffle import dance

def main(argv):
    Spot = CreateSpot.Robot(argv)
    try:
        with Spot.keepLeaseAlive():
            Spot.wake()
            #dance(Spot)
            Spot.stance(.3,.3)
            Spot.sleep()
    finally:
        Spot.getLease()

    print("Stopping")


if __name__ == '__main__':
    if not main(sys.argv[1:]):
        sys.exit(1)