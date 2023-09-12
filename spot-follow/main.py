import sys, VoiceCommands as VC
from CreateSpot import Robot

def main(argv):
    Spot = Robot(argv)
    try:
        with Spot.keepLeaseAlive():
            Spot.wake()
            # VC.accept_voice(Spot)
            Spot.stand(1)
            Spot.stand(.5)
            Spot.sleep()

    finally:
        Spot.getLease()

if __name__ == '__main__':
    if not main(sys.argv[1:]):
        sys.exit(1)