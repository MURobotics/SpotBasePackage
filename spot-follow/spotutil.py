import time
from enum import Enum, auto

#adds time.time() to duration
def get_command_duration(duration: float):
    return time.time() + duration

#duration in milliseconds (i think, im not gonna check)
def pause(duration:float):
    time.sleep(duration)

class Direction(Enum):
    LEFT=auto()
    RIGHT=auto()
    FORWARDS=auto()
    BACKWARDS=auto()

class RotationDirection(Enum):
    COUNTERCLOCKWISE = auto()
    CLOCKWISE = auto()

