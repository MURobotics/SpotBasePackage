import sys, VoiceCommands as VC
from CreateSpot import Robot
from spotutil import Camera

# from CameraStitching import stitch

def main(argv):
    Spot = Robot(argv)
    try:
        with Spot.keepLeaseAlive():
            Spot.wake()
            # commands must come after wake() and before sleep()
            # start commands

            # VC.accept_voice(Spot)
            # Spot.stand(1)
            # Spot.stand(.5)
            # Spot.turn(90, 2)
            # Spot.takeImage(Camera.FRONTLEFT, name="FrontLeft")
            # Spot.takeImage(Camera.FRONTRIGHT, name="FrontRight")
            # Spot.takeImage(Camera.LEFT, name=Camera.LEFT + ".jpg")
            # Spot.takeImage(Camera.RIGHT, name=Camera.RIGHT + ".jpg")
            # Spot.takeImage(Camera.BACK, name=Camera.BACK + ".jpg")

            # stitch(Spot.robot)

            Spot.selfie()
            
            # end commands
            Spot.sleep()

    finally:
        Spot.getLease()

if __name__ == '__main__':
    if not main(sys.argv[1:]):
        sys.exit(1)