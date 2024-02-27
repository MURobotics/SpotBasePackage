import sys

sys.path.append('..')
import socket
import random
import cv2 as cv                # type: ignore
from spotutil import FacePos
import datetime

HOST = '0.0.0.0'
PORT = 64532

images = 0


def find_face(image):
    # Read image from your local file system
    original_image = cv.imread(image)
    # Convert color image to grayscale for Viola-Jones
    grayscale_image = cv.cvtColor(original_image, cv.COLOR_BGR2GRAY)
    center = grayscale_image.shape[0] / 2
    # Load the classifier and create a cascade object for face detection

    front_face_cascade = cv.CascadeClassifier('haarcascade_frontalface_default.xml')
    side_face_cascade = cv.CascadeClassifier('haarcascade_profileface.xml')

    print("looking for front face...")
    detected_faces = front_face_cascade.detectMultiScale(grayscale_image)

    print("looking for face profile...")
    if len(detected_faces) == 0:
        detected_faces = side_face_cascade.detectMultiScale(grayscale_image)

    # get center point of square and detect distance from center of image
    # raise or lower spot angle until square-center is within certain threshhold of image center

    if len(detected_faces) > 0:
        total_y = 0
        for (column, row, width, height) in detected_faces:
            w2 = int(width / 2)
            h2 = int(height / 2)
            cv.rectangle(
                original_image,
                (column, row),
                (column + width, row + height), 
                (0, 255, 0),
                2
            )
            total_y = total_y + row + h2
        avg_y = total_y / len(detected_faces)

        r = random.random()
        r = str(r)
        rand = r.split(".")[1]
        cv.imwrite(f'../imgs/found/found_face-{datetime.datetime.now()}.jpg',original_image) 


        if abs(center - avg_y) < 100: return FacePos.CENTERED
        if avg_y > center: return FacePos.MOVEDOWN
        if avg_y < center: return FacePos.MOVEUP
    else:
        # try body checks

        body_caascades = {
            "full": cv.CascadeClassifier('haarcascade_fullbody.xml'),
            "upper": cv.CascadeClassifier('haarcascade_upperbody.xml'),
            "lower": cv.CascadeClassifier('haarcascade_lowerbody.xml'),
        }

        for label, caas in body_caascades.items():
            print(f"looking for {label} body...")
            detected_bodies = caas.detectMultiScale(grayscale_image)
            if len(detected_bodies) > 0: 
                print(f"{label} detected")
                break

        if len(detected_bodies) > 0:
            return FacePos.MOVEUP
        
        return FacePos.NOFACE
    
    return FacePos.NOFACE


def receive_image():
    # Receive the length of the image data
    length_bytes = connection.recv(4)
    length = int.from_bytes(length_bytes, byteorder='big')

    # Receive the image data
    image_data = b''
    while len(image_data) < length:
        data = connection.recv(length - len(image_data))
        if not data:
            break
        image_data += data
    
    return image_data

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to a specific address and port
server_address = (HOST, PORT)
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)

print("Waiting for a connection...")

while True:

    # Accept a connection
    connection, client_address = sock.accept()

    image_data = receive_image()

    # Save the image
    with open(f'../imgs/temp/received_image_{images}.jpg', 'wb') as image_file:
        image_file.write(image_data)


    print("Image received.")

    response = find_face(f'../imgs/temp/received_image_{images}.jpg')

    images += 1

    if (response != FacePos.NOFACE): 
        print("Face seen!")
    if (response == FacePos.MOVEUP):
        print("move up")
    if (response == FacePos.MOVEDOWN):
        print("move down")


    connection.sendall(response.value.to_bytes(4, byteorder='little'))

    # Close the connection and the socket
    connection.close()