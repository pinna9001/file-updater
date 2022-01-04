import socket
import hashlib

BUF_SIZE = 1024

INSTRUCTION_CLOSE = 0
INSTRUCTION_HASH = 1
INSTRUCTION_FILE = 2

def getHashOfFile(filename):
    md5 = hashlib.md5()
    with open(filename, 'rb') as f:
        while True:
            data=f.read(BUF_SIZE)
            if not data:
                break
            md5.update(data)
    return md5.digest()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.connect(("raspberrypi", 12345))


dataToSend = bytearray()
dataToSend.append(INSTRUCTION_HASH)
dataToSend += ("file.txt".encode("ascii"))
s.send(dataToSend)

data = s.recv(1024)

if not data:
    print("closed Connection.")
    exit()
if data == getHashOfFile("G:\\updater\\client\\file.txt"):
    print("current files are matching. Nothing will be updated.")
else: 
    print("Current files are not matching. The current file will be updated.")

dataToSend = bytearray()
dataToSend.append(INSTRUCTION_FILE)
dataToSend += ("file.txt".encode("ascii"))
s.send(dataToSend)

data = s.recv(1024)

fo = open("G:\\updater\\client\\file.txt", "wb")

fo.write(data)

s.close()