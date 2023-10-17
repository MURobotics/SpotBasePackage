import socket
import time
from tkinter import *

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 8080  # The port used by the server

standcommand = b'stand 1.0'
sitcommand = b'sit'
movecommand1 = b'move 0.0 1.0 1.0'
movecommand2 = b'move 1.0 0.0 2.0'
turncommand = b'turn 1.0 r 1.0'

def make_window() -> None:
    win = Tk()

    win.geometry("550x350")

    def sit():
        s.sendall(sitcommand)
        data = s.recv(1024)
        print(f"Received {data!r}")

    def stand():
        s.sendall(standcommand)
        data = s.recv(1024)
        print(f"Received {data!r}")

    Button(win, text="sit", command=lambda: sit()).pack()
    Button(win, text="stand", command=lambda: stand()).pack()

    def stop_program():
        win.destroy()
        
    Stop = Button(win, text="Exit", command=stop_program)
    Stop.pack()
    while True:
        win.update_idletasks()
        win.update()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    print('set up')
    s.connect((HOST, PORT))
    print('connected')
    make_window()