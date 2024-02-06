import cv2 as cv
from enum import Enum, auto


class FacePos(Enum):
    MOVEUP = auto()
    MOVEDOWN = auto()
    NOFACE = auto()
    CENTERED = auto()


def find_face(image):
    # Read image from your local file system
    original_image = cv.imread(image)

    # Convert color image to grayscale for Viola-Jones
    grayscale_image = cv.cvtColor(original_image, cv.COLOR_BGR2GRAY)

    center = grayscale_image.shape[0] / 2
    # print(height / 2)
    # print(center)

    # Load the classifier and create a cascade object for face detection
    face_cascade = cv.CascadeClassifier('haarcascade_frontalface_default.xml')

    detected_faces = face_cascade.detectMultiScale(grayscale_image)


    # get center point of square and detect distance from center of image
    # raise or lower spot angle until square-center is within certain threshhold of image center

    if len(detected_faces) == 0:
        return FacePos.NOFACE;
    else:
        total_y = 0
        for (column, row, width, height) in detected_faces:
            w2 = int(width / 2)
            # h2 = int(height / 2)
            # cv.rectangle(
            #     original_image,
            #     (column, row),
            #     (column + w2, row + h2), 
            #     (0, 255, 0),
            #     2
            # )
            # cv.rectangle(
            #     original_image,
            #     (column, row),
            #     (column + width, row + height),
            #     (0, 255, 0),
            #     2
            # )
            total_y = total_y + column + w2 #using width rn because image is tilted
            # print((column + width, row + height))
        avg_y = total_y / len(detected_faces)
        if abs(center - avg_y) < 100: return FacePos.CENTERED
        if avg_y < center: return FacePos.MOVEDOWN
        if avg_y > center: return FacePos.MOVEUP

    # cv.imshow('Image', original_image)
    # cv.waitKey(0)
    # cv.destroyAllWindows()



    
# print(find_face('./pic1.png'))


import re, socket
from CreateSpot import Robot


HOST = ""
PORT = 64532

def accept_voice(Spot: Robot):
    '''
        Opens a connection on to the port 64532 to listen for commands from the VoiceRegognition program.
    '''

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        conn, addr = s.accept()
        with conn:
            print(f"Connected by {addr}")
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                if parse_command(Spot, data.decode('utf-8')):
                    conn.sendall(b"Successful")
                elif data == b"Exit":
                    return
                else: conn.sendall(b"Error")


def parse_command(Spot: Robot, command: str) -> bool:
    command = command.split(" ")

    if command[0] == "sit":
        Spot.sit()
    elif command[0] == "stand":
        Spot.stand(float(command[1]))
    else:
        return False
    
    return True




# with mic as source:
#     r.adjust_for_ambient_noise(source)
#     audio = r.listen(source)

# print(r.recognize_google(audio))




# def accept_voice(Spot):
#     r = sr.Recognizer()
#     mic = sr.Microphone()
#     input("Hello! press enter to capture your voice!")
#     with mic as source:
#         r.adjust_for_ambient_noise(source)
#         audio = r.listen(source)
#         word = r.recognize_google(audio)
#         print(word)

#     if re.search(r"Spot sit", word, re.I) or re.search(r"spot set", word, re.I):
#         send("sit")
#         # Spot.sit()
#     elif re.search(r"Spot stand", word, re.I):
#         send("stand")
#         # Spot.stand()
#     elif re.search(r"Spot walk", word, re.I):
#         send("walk 5")
#     elif r.search(r"Spot turn left", word, re.I):
#         send("turn 90")
#     elif r.search(r"Spot turn right", word, re.I):
#         send("turn -90")
#     else:
#         print(word)
    

# def send(msg: str):
#     #   do whatever needs to happen
#     print(msg)

# accept_voice(None)
