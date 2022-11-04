import time
from enum import Enum, auto

def get_command_duration(duration: float) -> float:
    return time.time() + duration

class Direction(Enum):
    LEFT=auto()
    RIGHT=auto()
    FORWARDS=auto()
    BACKWARDS=auto()

