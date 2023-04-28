import sys, VoiceCommands as VC
from CreateSpot import Robot

def main(argv):
    Spot = Robot(argv)
    try:
        with Spot.keepLeaseAlive():
            VC.accept_voice(Spot)

    finally:
        Spot.getLease()

if __name__ == '__main__':
    if not main(sys.argv[1:]):
        sys.exit(1)
