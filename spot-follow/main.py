import sys, VoiceCommands as VC
from CreateSpot import Robot
from spotutil import Camera

def main(argv):
    Spot = Robot(argv)
    try:
        with Spot.keepLeaseAlive():
            Spot.wake()
            # VC.accept_voice(Spot)
            # Spot.stand(1)
            # Spot.stand(.5)
            # Spot.turn(90, 2)
            # Spot.takeImage(Camera.FRONTLEFT, name=Camera.FRONTLEFT + ".jpg")
            # Spot.takeImage(Camera.FRONTRIGHT, name=Camera.FRONTRIGHT + ".jpg")
            # Spot.takeImage(Camera.LEFT, name=Camera.LEFT + ".jpg")
            # Spot.takeImage(Camera.RIGHT, name=Camera.RIGHT + ".jpg")
            # Spot.takeImage(Camera.BACK, name=Camera.BACK + ".jpg")

            Spot.selfie()
            Spot.sleep()

    finally:
        Spot.getLease()

if __name__ == '__main__':
    if not main(sys.argv[1:]):
        sys.exit(1)