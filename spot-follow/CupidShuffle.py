import CreateSpot as spot
from CreateSpot import Robot
import SpotUtil as util
from SpotUtil import Direction, RotationDirection

#The command to perform the Cupid Shuffle
def dance(robot : Robot) -> None:
    print("Starting dance sequence")

    #print(f"3, {util.get_command_duration(3.0)}")
    #dance_step(robot, Direction.RIGHT, 4, 3.0)
    #dance_step(robot, Direction.LEFT, 4, 3.0)
    dance_spin(robot, 90.0, 3.0)

    print("Dancing sequence finished")

#Given a direction, it will make a certain number of steps in that direction 
#in a given amount of time
def dance_step(robot : Robot, direction : Direction, steps : int, duration = 0.0) -> None:
    print(f"Moving {direction.name}")

    #ideally, this loop would make spot go at a speed that
    #it can step exactly three steps either left or right
    #given the right parameters
    # for i in range(0, steps):
    #     robot.strafe(0.5, direction, duration/steps)

    robot.strafe(0.3, direction, duration)

#Given an amount of degrees to spin, it will spin in a given time period
def dance_spin(robot : Robot, degrees : float, duration : float) -> None:
    print(f"Spinning {degrees}")

    robot.trajectory(0,0, degrees, duration = duration)





