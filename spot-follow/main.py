# Copyright (c) 2021 Boston Dynamics, Inc.  All rights reserved.
#
# Downloading, reproducing, distributing or otherwise using the SDK Software
# is subject to the terms and conditions of the Boston Dynamics Software
# Development Kit License (20191101-BDSDK-SL).

"""Tutorial to show how to use the Boston Dynamics API"""
from __future__ import print_function
from tkinter import *
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
from CupidShuffle import dance

def make_window(robot : Robot) -> None:
    win = Tk()

    win.geometry("550x350")

    def stand(robot : Robot):
        robot.stand(1.0)

    def sit(robot : Robot):
        robot.sit()

    Button(win, text="sit", command=lambda: sit(robot)).pack()
    Button(win, text="stand", command=lambda: stand(robot)).pack()

    def stop_program():
        win.destroy()
        
    Stop = Button(win, text="Exit", command=stop_program)
    Stop.pack()
    while True:
        win.update_idletasks()
        win.update()

def main(argv):
    Spot = Robot(argv)
    try:
        with Spot.keepLeaseAlive():
            Spot.wake()
            make_window(Spot)
            #dance(Spot)
            #Spot.stance(.3,.3)
            Spot.sleep()
    finally:
        Spot.getLease()

    print("Stopping")
    #make_window()


if __name__ == '__main__':
    if not main(sys.argv[1:]):
        sys.exit(1)