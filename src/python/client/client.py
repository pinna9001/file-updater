import socket
import hashlib
import os
import sys

BUF_SIZE = 1024

INSTRUCTION_CLOSE = 0
INSTRUCTION_HASH = 1
INSTRUCTION_FILE = 2

RETURN_VALUE_FILE_DOESNT_EXIST = 8

def getHashOfFile(filename):
    if not os.path.exists(filename):
        return None
    md5 = hashlib.md5()
    with open(filename, 'rb') as f:
        while True:
            data=f.read(BUF_SIZE)
            if not data:
                break
            md5.update(data)
    return md5.digest()


# returns the requested Filehash or None,
# if the file doesnt exist on the server
def requestFileHash(socket, filename):
    dataToSend = bytearray()
    dataToSend.append(INSTRUCTION_HASH)
    dataToSend += (filename.encode("ascii"))
    socket.send(dataToSend)

    recv = socket.recv(1024)
    if not recv:
        print("closed connection")
        exit()
    elif int.from_bytes(recv, byteorder='big') == RETURN_VALUE_FILE_DOESNT_EXIST:
        return None
    else:
        return recv

def checkForUpdates(directoryPath):
    if not os.path.exists(directoryPath):
        print("specified path does not exist. ")
        exit()
    relativePathToAllFiles = [os.path.relpath(os.path.join(r, file), directoryPath) for r, s, f in os.walk(directoryPath) for file in f]

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("localhost", 12345))
    for filepath in relativePathToAllFiles:
        filepath = filepath.replace(os.path.sep, "/")
        fileHash = requestFileHash(s, filepath)
        print(filepath)
        if fileHash == None:
            print("file doesn't exist on server. File will be deleted.")
            os.remove(os.path.join(directoryPath, filepath))
        elif fileHash == getHashOfFile(os.path.join(directoryPath, filepath)):
            print("Current files are matching. Nothing will be updated.")
        else:
            print("Current files are not matching. The existing file will be updated.")

            dataToSend = bytearray()
            dataToSend.append(INSTRUCTION_FILE)
            dataToSend += (filepath.encode("ascii"))
            s.send(dataToSend)

            data = s.recv(1024)

            fo = open(os.path.join(directoryPath, filepath), "wb")

            fo.write(data)

    s.close()

if __name__ == "__main__":
    checkForUpdates(sys.argv[1])
