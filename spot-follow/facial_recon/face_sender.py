import socket
import sys
sys.path.append('..')
from spotutil import FacePos

HOST = socket.gethostbyname('host.docker.internal')
PORT = 64532

def find_face(file_name="temp-img.jpg", file_path="/usr/src/app/imgs/"):
    '''
        Parameters:
            file_name: The name of the file.'
            file_path: The location of the file.'

            Under normal use thse values should not be changed

        Returns:
            spotutil.FacePos
    '''
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect the socket to the server's address and port
    server_address = (HOST, PORT)
    sock.connect(server_address)

    # Open the image file in binary mode
    with open(f'{file_path}{file_name}', 'rb') as image_file:
        # Read the binary data
        image_data = image_file.read()

    # Send the length of the image data
    length = len(image_data)
    sock.sendall(length.to_bytes(4, byteorder='big'))

    # Send the image data
    sock.sendall(image_data)

    response_bytes = sock.recv(4)
    response_value = int.from_bytes(response_bytes, byteorder='little')
    response = FacePos(response_value)

    # Close the socket
    sock.close()

    return response
