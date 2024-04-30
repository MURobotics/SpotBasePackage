
import time
from enum import Enum, auto
from math import pi

#adds time.time() to duration, required for timed commands
def get_command_duration(duration: float):
    return time.time() + duration

#duration in milliseconds (i think, im not gonna check)
def pause(duration:float):
    time.sleep(duration)

def deg_to_rad(degrees: float):
    return degrees * (pi/180)

#Enums for ease of imputting direction into movement commands
class Direction(Enum):
    LEFT = auto()
    RIGHT = auto()
    FORWARDS = auto()
    BACKWARDS = auto()

class RotationDirection(Enum):
    COUNTERCLOCKWISE = auto()
    CLOCKWISE = auto()

class Leg(Enum):
    FRONT_LEFT = auto()
    FRONT_RIGHT = auto()
    BACK_LEFT = auto()
    BACK_RIGTH = auto()

class Camera(str, Enum):
    BACK = 'back_fisheye_image'
    FRONTLEFT = 'frontleft_fisheye_image'
    FRONTRIGHT = 'frontright_fisheye_image'
    LEFT = 'left_fisheye_image'
    RIGHT = 'right_fisheye_image'

