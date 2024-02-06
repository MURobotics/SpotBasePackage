from __future__ import print_function
import argparse
import sys
import time
import os
import bosdyn.client
import bosdyn.client.lease
import bosdyn.client.util
import bosdyn.geometry as geometry
import SpotUtil as util

from bosdyn.client import frame_helpers, math_helpers
from bosdyn.client.image import ImageClient
from bosdyn.client.robot_command import RobotCommandBuilder, RobotCommandClient, blocking_stand
from bosdyn.api.basic_command_pb2 import RobotCommandFeedbackStatus
from bosdyn.client.math_helpers import Vec2
from bosdyn.client.robot_state import RobotStateClient
from bosdyn.client.frame_helpers import BODY_FRAME_NAME, ODOM_FRAME_NAME, VISION_FRAME_NAME

# for image processing
from PIL import Image
import io

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
        #New
        parser.add_argument('--x-offset', default=0.5, type=float, help='Offset in X for Spot to step')
        parser.add_argument('--y-offset', default=0.4, type=float, help="Offset in Y for Spot to step")
        #end new
        options = parser.parse_args(argv)
        try:
            self.run(options)
        except Exception as exc:
            self.err("Hello, Spot threw an exception: %r", exc)


    # run() connects to the spot robot and sets up time sync
    # If there are issues connecting, ensure the spot_account.env file in the secrets folder is properly formatted with correct credentials
    # run() is run automatically upon initializing the Robot class
    def run(self, config):
        self.config = config
        bosdyn.client.util.setup_logging(config.verbose)  
        self.sdk = bosdyn.client.create_standard_sdk('HelloSpotClient')
        self.robot = self.sdk.create_robot(config.hostname)
        self.robot.authenticate(config.username, config.password)
        self.robot.time_sync.wait_for_sync()
        assert not self.robot.is_estopped(), "Robot is estopped. Please use an external E-Stop client, " \
                                        "such as the estop SDK example, to configure E-Stop."  
        self.lease_client = self.robot.ensure_client(bosdyn.client.lease.LeaseClient.default_service_name)
        self.lease = self.lease_client.acquire()

        #NEW
        self.state = self.robot.ensure_client(RobotStateClient.default_service_name).get_robot_state()


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
        print("command called")
        self.command_client.robot_command(cmd, duration)
        self.delay(delay);

    # delay() is delay between commands. Defaults to default_delay value [set with setDefaultDelay(). default is 3]
    # all functions take delay parameter, if none is given it defaults to None which is then replaced with the default value
    def delay(self, delay=None):
        # delay = delay if delay else self.default_delay
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
    
    # head_up() causes the robot to move its head up while standing at a given height
    # height is in meters, pitch is in degrees (negative means head moves up)
    def head_up(self, pitch, height, delay=None):
        self.command(
            RobotCommandBuilder.synchro_stand_command(body_height=height, 
                                                      footprint_R_body=geometry.EulerZXY(pitch=util.deg_to_rad(pitch))),
            delay    
        )

    # x and y are in meters relative to Spot (x is forward)
    def trajectory(self, x=0.0, y=0.0, heading=0.0, duration=0, delay=None):
        self.command(
            RobotCommandBuilder().synchro_trajectory_command_in_body_frame(x, y, heading, self.robot.get_frame_tree_snapshot()),
            delay,
            util.get_command_duration(duration)
        )

    # standing turn
    # takes degrees and turn duration and rotates spot in place
    def turn(self, degrees, duration, delay=None):
        self.command(
            RobotCommandBuilder.synchro_velocity_command(v_x=0.0, v_y=0.0, v_rot=util.deg_to_rad(degrees)),
            delay=delay,
            duration=util.get_command_duration(duration)
        )

    #takes a picture from the inputed camera
    def takeImage(self, camName: util.Camera, path="./imgs/"):
        image_client = self.robot.ensure_client(ImageClient.default_service_name)
        image_response = image_client.get_image_from_sources([camName.value])
        image = image_response[0].shot.image

        name = "spot-img.jpg"
        if path is not None and os.path.exists(path):
            path = os.path.join(os.getcwd(), path)
            name = os.path.join(path, name)
            print("attempt save image to: {}".format(name))
        else:
            print("possibly invalid path, attempting save anyway")
            print("attempt save image to {}".format(name))
        try:
            image = Image.open(io.BytesIO(image.data))
            image.save(name)
        except Exception as exc:
            print("exception thrown saving image. %r", exc)


    def selfie(self):
        self.pose_body(pitch=util.deg_to_rad(-45))
        self.takeImage(util.Camera.FRONTLEFT)

    def getRobotStateClient(self):
        return self.robot.ensure_client(RobotStateClient.default_service_name)
    
    def getRobotCommandClient(self):
        return self.robot.ensure_client(RobotCommandClient.default_service_name)

    def getRobotState(self):
        return self.robot.ensure_client(RobotStateClient.default_service_name).get_robot_state()

    #Helper function for stance_movement
    def getOdomPosition(self):
        return frame_helpers.get_se2_a_tform_b(self.getRobotState().kinematic_state.transforms_snapshot,
                                                frame_helpers.ODOM_FRAME_NAME,
                                                frame_helpers.GRAV_ALIGNED_BODY_FRAME_NAME)

    #Moves Spot's feet
    #Takes in a list where its the x and y offset for [front left, front right, back left, back right]
    #x_offset should be between .2 and .5; y_offset should be between .1 and .4
    def stance_movement(self, offset : list, delay = 1.0) -> None:
        body_state = self.getOdomPosition()
        pos_fl_rt_vision = body_state * math_helpers.SE2Pose(offset[0][0], offset[0][1], 0)
        pos_fr_rt_vision = body_state * math_helpers.SE2Pose(offset[1][0], -offset[1][1], 0)
        pos_hl_rt_vision = body_state * math_helpers.SE2Pose(-offset[2][0], offset[2][1], 0)
        pos_hr_rt_vision = body_state * math_helpers.SE2Pose(-offset[3][0], -offset[3][1], 0)

        stance_cmd = RobotCommandBuilder.stance_command(
                frame_helpers.ODOM_FRAME_NAME, 
                pos_fl_rt_vision.position, 
                pos_fr_rt_vision.position,
                pos_hl_rt_vision.position, 
                pos_hr_rt_vision.position            
            )

        stance_cmd.synchronized_command.mobility_command.stance_request.end_time.CopyFrom(
                   self.robot.time_sync.robot_timestamp_from_local_secs(util.get_command_duration(5)))

        self.command(stance_cmd, delay = delay)
    
    #Move Spot relative to where it is (dx and dy are in meters, dyaw is in degrees ccw)
    def relative_move(self, dx, dy, dyaw, frame_name, stairs=False):
        robot_state = self.getRobotState()
        robot_command_client = self.getRobotCommandClient()
        transforms = robot_state.kinematic_state.transforms_snapshot

        # Build the transform for where we want Spot to be relative to where the body currently is.
        body_tform_goal = math_helpers.SE2Pose(x=dx, y=dy, angle=dyaw)
        out_tform_body = frame_helpers.get_se2_a_tform_b(transforms, frame_name, frame_helpers.BODY_FRAME_NAME)
        out_tform_goal = out_tform_body * body_tform_goal

        # Command the robot to go to the goal point in the specified frame. The command will stop at the new position.
        robot_cmd = RobotCommandBuilder.synchro_se2_trajectory_point_command(
            goal_x=out_tform_goal.x, goal_y=out_tform_goal.y, goal_heading=out_tform_goal.angle,
            frame_name=frame_name, params=RobotCommandBuilder.mobility_params(stair_hint=stairs))
        end_time = 10.0
        cmd_id = robot_command_client.robot_command(lease=None, command=robot_cmd,
                                                    end_time_secs=util.get_command_duration(end_time))
        # Wait until the robot has reached the goal.
        while True:
            feedback = robot_command_client.robot_command_feedback(cmd_id)
            mobility_feedback = feedback.feedback.synchronized_feedback.mobility_command_feedback
            if mobility_feedback.status != RobotCommandFeedbackStatus.STATUS_PROCESSING:
                print(f'Failed to reach the point {dx}, {dy}, {dyaw}')
                return False
            traj_feedback = mobility_feedback.se2_trajectory_feedback
            if (traj_feedback.status == traj_feedback.STATUS_AT_GOAL and
                    traj_feedback.body_movement_status == traj_feedback.BODY_STATUS_SETTLED):
                print(f'Arrived at the point {dx}, {dy}, {dyaw}')
                return True
            time.sleep(1)

        return True
    
    #Move spot based on a list of points in the form (x,y,heading)
    #Points are listed out where Spot is relative to it after it moved to all previous points
    def relative_point_movement(self, orien_points:list, frame_name):
        for point in orien_points:
            self.relative_move(point[0],
                               point[1],
                               point[2],
                               frame_name)

    #Move spot based on a list of points in the form (x,y,heading)
    #Points are listed out where Spot is relative to it at the start of the function call
    #init_position = [x position, y position, heading (in degrees; positive ccw)]
    def global_point_movement(self, orien_points:list, frame_name = ODOM_FRAME_NAME, init_position = None):
        if init_position is None:
            global_x = 0; global_y = 0; global_w = 0
        else:
            global_x = init_position[0]; global_y = init_position[1]; global_w = init_position[2]

        for point in orien_points:
            rel_x = point[0] - global_x; rel_y = point[1] - global_y;  rel_w = point[2] - global_w

            self.relative_move(rel_x, rel_y, rel_w, frame_name)
            
            global_x += rel_x; global_y += rel_y; global_w += rel_w
            
        return global_x, global_y, global_w