from __future__ import print_function
import argparse
import sys
import time
import os
import bosdyn.client
import bosdyn.client.lease
import bosdyn.client.util
import bosdyn.geometry
import SpotUtil as util
from SpotUtil import Direction, RotationDirection

from bosdyn.client import frame_helpers, math_helpers
from bosdyn.client.robot_state import RobotStateClient
from bosdyn.client.image import ImageClient
from bosdyn.client.robot_command import RobotCommandBuilder, RobotCommandClient, blocking_stand

#   [docker-compose build] while connected to wifi to compile
#   [docker-compose up] while connected to spot to run

class Robot:
    #   -----   Startup commands    -----

    # __init__() initializes starting values and uses the run() function to connect to spot
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

    def log(self, info):
        self.robot.logger.info(info)

    def err(self, info, *args):
        self.robot.logger.error(info, args)

    def getLease(self):
        return self.lease_client.return_lease(self.lease)

    def getLeaseClient(self):
        return self.lease_client

    # keepLeaseAlive() used in try statement around Spot commands. Prevents other users from taking control.
    def keepLeaseAlive(self):
        return bosdyn.client.lease.LeaseKeepAlive(self.lease_client)

    # setDefaultDelay() sets the delay used if none is given in movement commands.
    def setDefaultDelay(self, delay):
        self.default_delay = delay

    #   -----   Movement Commands   -----   #

    def command(self, cmd, delay=None, duration=None):
        self.command_client.robot_command(cmd, duration)
        self.delay(delay)

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
    def trajectory(self, x=0.0, y=0.0, heading=0.0, duration=0, delay=None):
        self.command(
            RobotCommandBuilder().synchro_trajectory_command_in_body_frame(x, y, heading, self.robot.get_frame_tree_snapshot()),
            delay,
            util.get_command_duration(duration)
        )

    #Runs a synchro velocity command
    def move_velocity(self, v_x=0.0, v_y=0.0, v_rot=0.0, duration=0.0):
        print(f"{time.time()}, {util.get_command_duration(3.0)}")
        self.command(
            RobotCommandBuilder.synchro_velocity_command(
                v_x=v_x,
                v_y=v_y,
                v_rot=v_rot
            ),
            duration = util.get_command_duration(duration)
        )
    
    #Runs a synchro trajectory command
    #heading in radians, postion relative to robot frame
    def move_position(self, x_pos=0.0, y_pos=0.0, heading=0.0, duration=0.0):
        self.command(
            RobotCommandBuilder.synchro_trajectory_command_in_body_frame(
                goal_x_rt_body = x_pos, 
                goal_y_rt_body = y_pos, 
                goal_heading_rt_body = heading
            ),
            duration = util.get_command_duration(duration)
        )

    #Moves left or right
    def strafe(self, speed: float, direction: Direction, duration=0.0):
        if (not (direction is Direction.LEFT or direction is Direction.RIGHT)):
            print("No strafing?")
            raise Exception("Invalid direction for strafing")

        speed = speed if direction is Direction.LEFT else -speed
        self.move_velocity(0, speed, 0, duration)

    #Moves forwards or backwards
    def walk(self, speed: float, direction: Direction, duration=0.0):
        if (not (direction is Direction.FORWARDS or direction is Direction.BACKWARDS)):
            print("No walking?")
            raise Exception("Invalid direction for walking")

        speed = speed if direction is Direction.FORWARDS else -speed
        self.move_velocity(speed, 0, 0, duration)

    #Rotates counterclockwise or clockwise
    def rotate(self, rot_speed: float, rot_direction: RotationDirection, duration = 0.0):
        rot_speed = rot_speed if rot_direction is RotationDirection.COUNTERCLOCKWISE else -rot_speed
        self.move_velocity(0, 0, rot_speed, duration)

    def getRobotState(self):
        return self.robot.ensure_client(RobotStateClient.default_service_name).get_robot_state()

    #Helper function for stance
    def getBodyPosition(self):
        return frame_helpers.get_se2_a_tform_b(self.getRobotState().kinematic_state.transforms_snapshot,
                                                frame_helpers.VISION_FRAME_NAME,
                                                frame_helpers.GRAV_ALIGNED_BODY_FRAME_NAME)

    #x_offset should be between .2 and .5; y_offset should be between .1 and .4
    def stance(self, x_offset: float, y_offset: float):
        body_state = self.getBodyPosition()
        pos_fl_rt_vision = body_state * math_helpers.SE2Pose(x_offset, y_offset, 0)
        pos_fr_rt_vision = body_state * math_helpers.SE2Pose(x_offset, -y_offset, 0)
        pos_hl_rt_vision = body_state * math_helpers.SE2Pose(-x_offset, y_offset, 0)
        pos_hr_rt_vision = body_state * math_helpers.SE2Pose(-x_offset, -y_offset, 0)

        stance_cmd = RobotCommandBuilder.stance_command(
                frame_helpers.VISION_FRAME_NAME, 
                pos_fl_rt_vision.position, 
                pos_fr_rt_vision.position,
                pos_hl_rt_vision.position, 
                pos_hr_rt_vision.position            
            )

        stance_cmd.synchronized_command.mobility_command.stance_request.end_time.CopyFrom(
                   self.robot.time_sync.robot_timestamp_from_local_secs(util.get_command_duration(5)))

        self.command(stance_cmd, delay = 1)
    


