import socket

HOST = "server"  # The server's hostname or IP address
PORT = 65432  # The port used by the server

standcommand = b'stand 1.0'
sitcommand = b'sit'
movecommand1 = b'move 0.0 1.0 1.0'
movecommand2 = b'move 1.0 0.0 0.5'
turncommand = b'turn l 1.0 1.0'

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(standcommand)
    data = s.recv(1024)
    print(f"Received {data!r}")
    s.sendall(sitcommand)
    data = s.recv(1024)
    print(f"Received {data!r}")
    s.sendall(movecommand1)
    data = s.recv(1024)
    print(f"Received {data!r}")
    s.sendall(movecommand2)
    data = s.recv(1024)
    print(f"Received {data!r}")
    s.sendall(turncommand)
    data = s.recv(1024)
    print(f"Received {data!r}")