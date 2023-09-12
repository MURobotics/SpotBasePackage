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
