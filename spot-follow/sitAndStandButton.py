# Import the required libraries
from tkinter import *
from time import sleep
import os
import sys
# Create an instance of tkinter frame or window

def make_window():

    if os.environ.get('DISPLAY','') == '':
        print('no display found. Using :0:0')
        os.environ.__setitem__('DISPLAY', ':0:0')

    win=Tk()

    # Set the size of the tkinter window
    win.geometry("550x350")

    def stand():
        print("stand")

    def sit():
        print("sit")


    # Cmd_Que_Label=Label(win, text="Action list so far: ", font=('Calibri 15'))
    # Cmd_Que_Label.pack(pady=20)
    Button(win, text="sit", command=sit).pack()
    Button(win, text="stand", command=stand).pack()


    def stop_program():
        win.destroy()
        
    Stop = Button(win, text="Exit the program", command=stop_program)
    Stop.pack()

    while True:
        win.update_idletasks()
        win.update()

        
# make_window()

