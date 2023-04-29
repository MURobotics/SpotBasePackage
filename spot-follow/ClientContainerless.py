import socket
import time

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 8080  # The port used by the server

standcommand = b'stand 1.0'
sitcommand = b'sit'
movecommand1 = b'move 0.0 1.0 1.0'
movecommand2 = b'move 1.0 0.0 2.0'
turncommand = b'turn 1.0 r 1.0'

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    print('set up')
    s.connect((HOST, PORT))
    print('connected')
    s.sendall(standcommand)
    print('sent')
    data = s.recv(1024)
    print(f"Received {data!r}")
    s.sendall(sitcommand)
    data = s.recv(1024)
    print(f"Received {data!r}")
    s.sendall(standcommand)
    data = s.recv(1024)
    print(f"Received {data!r}")
    s.sendall(movecommand2)
    data = s.recv(1024)
    print(f"Received {data!r}")
    s.sendall(turncommand)
    data = s.recv(1024)
    print(f"Received {data!r}")