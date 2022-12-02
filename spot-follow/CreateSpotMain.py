import sys
import CreateSpot as Create

def main(argv):
    Spot = Create.Robot(argv)
    try:
        with Spot.keepLeaseAlive():
            Spot.wake()
            Spot.stand(0.1)
            Spot.stand(0.005)
            Spot.sleep()
    finally:
        Spot.getLease()

if __name__ == '__main__':
    if not main(sys.argv[1:]):
        sys.exit(1)