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
        print("Closed connection")
        exit()
    elif int.from_bytes(recv, byteorder='big') == RETURN_VALUE_FILE_DOESNT_EXIST:
        return None
    else:
        return recv

def updateFile(socket, directoryPath, filepath):
    print(filepath, ": \n\tFiles are not matching. Updating...")
    dataToSend = bytearray()
    dataToSend.append(INSTRUCTION_FILE)
    dataToSend += (filepath.encode("ascii"))
    socket.send(dataToSend)

    fo = open(os.path.join(directoryPath, filepath), "wb")

    data = socket.recv(1024)

    fo.write(data)
    print("\tDone updating")

def checkFilePathForUpdatesAvailable(socket, directoryPath, filepath):
    fileHash = requestFileHash(socket, filepath)
    if fileHash == None:
        print(filepath, ": \n\tFiles does not exist on server. Deleting...")
        os.remove(filepath)
        return False
    elif fileHash == getHashOfFile(os.path.join(directoryPath, filepath)):
        print(filepath, ": \n\tFiles are matching.")
        return False
    else:
        return True

def checkForUpdates(directoryPath):
    if not os.path.exists(directoryPath):
        print(directoryPath, ": \n\tPath does not exist. Specify a existing path.")
        exit()

    relativePathToAllFiles = [os.path.relpath(os.path.join(r, file), directoryPath) for r, s, f in os.walk(directoryPath) for file in f]

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("localhost", 12345))

    for filepath in relativePathToAllFiles:
        filepath = filepath.replace(os.path.sep, "/")
        if checkFilePathForUpdatesAvailable(s, directoryPath, filepath):
            updateFile(s, directoryPath, filepath)

    s.close()

def printHelp():
    print("Help")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        printHelp()
        exit()
    if sys.argv[1] == "-h":
        printHelp()
    else:
        checkForUpdates(sys.argv[1])
