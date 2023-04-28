import speech_recognition as sr
import socket, re

#   Socket connection variables
HOST = socket.gethostname()
PORT = 64532

#   Speech recognition variables
recon = sr.Recognizer()
mic = sr.Microphone()

#   List of valid words and their associated command prompt
commands = [
    ["sit | set", "sit"],
    ["stand", "stand 3.0"],
    ["walk", "move 5.0 5.0 5.0"],
    ["turn left", "turn L 4.0 4.0"],
    ["turn right", "turn R 4.0 4.0"]
]


def accept_voice():
    '''
        Prompts the user to begin speaking then uses the SpeechRecognition library to get a string version.
        Uses regex to check if the string is a valid command then send the command to the spot server application.
    '''
    #   Prompt to make sure user is ready to speak
    input("Press enter to capture your voice!")
    #   Accesses the users default microphone and begins recording
    with mic as source:
        #   Helps prevent ambient noise from causing false positives/negatives
        recon.adjust_for_ambient_noise(source)
        #   Begins recording
        audio = recon.listen(source)
        #   Analyzes the recorded audio using the google speech recognition
        word = recon.recognize_google(audio)
        print(word)

    #   Check if command begins with the word SPOT
    if not re.search(r"^spot", word, re.I): 
        print(word)
        return

    #   Check command against valid commands
    for command in commands:
        if re.search(rf"{command[0]}", word, re.I):
            print(command[1])
            send(command[1])
            break
    else:
        print("Command not recognized. Please try again.")
        accept_voice()

    cont = input("Press (Y) to give another command, anything else to close")
    if cont == "Y" | cont == "y":
        accept_voice()
    else:
        send("Exit")
    

def send(msg: str):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(bytes(msg, 'utf-8'))
        data = s.recv(1024)

        if (data == b"Successful"):
            print("Command run successfully!")
        else:
            print("Command unsuccessful.")

accept_voice()






    # if re.search(r"sit | set", word, re.I):
    #     send("sit")
    # elif re.search(r"stand", word, re.I):
    #     send("stand")
    # elif re.search(r"walk", word, re.I):
    #     send("walk 5")
    # elif re.search(r"turn left", word, re.I):
    #     send("turn 90")
    # elif re.search(r"turn right", word, re.I):
    #     send("turn -90")
    # else:
    #     print(word)
