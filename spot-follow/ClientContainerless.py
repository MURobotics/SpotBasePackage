import socket
import time
from tkinter import *
import numbers

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 8080  # The port used by the server

standcommand = b'stand 1.0'
sitcommand = b'sit'
headtiltdowncommand = b'headtilt 45 1.0'
headtiltupcommand = b'headtilt -45 1.0'
resetcommand = b'headtilt 0 1.0'
movecommand1 = b'move 0.0 1.0 1.0'
movecommand2 = b'move 1.0 0.0 2.0'
turncommand = b'turn 1.0 r 1.0'
globalpointcommandheader = b'gmove'
stack_points = []

def make_window() -> None:
    win = Tk()

    win.geometry("550x350")

    #Image Label
    image_panel = Label(win)

    def sit():
        s.sendall(sitcommand)
        data = s.recv(1024)
        print(f"Received {data!r}")

    def stand():
        s.sendall(standcommand)
        data = s.recv(1024)
        print(f"Received {data!r}")

    def head_tilt_up():
        s.sendall(headtiltupcommand)
        data = s.recv(1024)
        print(f"Received {data!r}")
    def head_tilt_down():
        s.sendall(headtiltdowncommand)
        data = s.recv(1024)
        print(f"Received {data!r}")

    def reset_tilt():
        s.sendall(resetcommand)
        data = s.recv(1024)
        print(f"Received {data!r}")

    def global_point_movement():
        global stack_points, position
        command = globalpointcommandheader + f' {len(stack_points)}'.encode('utf-8')
        for point in stack_points:
            #x,y,heading
            command += f' {point[0]} {point[1]} {point[2]}'.encode('utf-8')
        s.sendall(command)
        data = s.recv(1024)
        print(f"{command!r}")
        print(f"Received {data!r}")

    def add_point():
        global stack_points

        point_arr = input_point.get(1.0, "end-1c").split()
        if(len(point_arr) == 3):
            all_numbers = True
            point = []
            for num in point_arr:
                num = int(num)
                all_numbers = (isinstance(num, numbers.Number) and not isinstance(num, bool)) and all_numbers
                point.append(num)
            if all_numbers:
                stack_points.append(point)
                update_stack_text()

    def remove_point():
        global stack_points

        stack_points.pop()
        update_stack_text()

    def update_stack_text():
        text = ""
        
        global stack_points
        for point in stack_points:
            text += f"({point[0]}, {point[1]}, {point[2]})\n"
        stack_text.config(text = text)
    
    # create listbox object
    listbox = Listbox(win, height = 10, 
                      width = 15, 
                      bg = "grey",
                      activestyle = 'dotbox', 
                      font = "Helvetica",
                      fg = "yellow")

    Button(win, text="sit", command=lambda: sit()).pack()
    Button(win, text="stand", command=lambda: stand()).pack()
    Button(win, text="head tilt up", command=lambda: head_tilt_up()).pack()
    Button(win, text="head tilt down", command=lambda: head_tilt_down()).pack()
    Button(win, text="reset stance", command=lambda: reset_tilt()).pack()

    #Global points stack
    input_point = Text(win, height = 2, width=10)
    input_point.pack()
    Button(win, text="Put onto queue", command=lambda: add_point()).pack()
    Button(win, text="Pull off queue", command=lambda: remove_point()).pack()
    stack_text = Label(win, text = "Global points stack")
    Button(win, text="Move", command=lambda: global_point_movement()).pack()
    stack_text.pack()

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