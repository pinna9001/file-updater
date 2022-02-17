import socket
import hashlib
import os
import sys
import re

# get from server
BUFF_SIZE = 1024

INSTRUCTION_CLOSE = 0
INSTRUCTION_CONFIG = 1
INSTRUCTION_HASH = 2
INSTRUCTION_REQUEST_FILE = 4
INSTRUCTION_UPDATE_FILE = 8
INSTRUCTION_VERSIONS = 16

RETURN_VALUE_FILE_DOESNT_EXIST = 1
RETURN_VALUE_FILE = 2
RETURN_VALUE_FILE_END = 4
RETURN_VALUE_HASH = 8
RETURN_VALUE_FILE_LIST = 16
RETURN_VALUE_VERSION_LIST = 32

safemode = False
updating = True

def getHashOfFile(filename):
    if not os.path.exists(filename):
        return None
    md5 = hashlib.md5()
    with open(filename, 'rb') as f:
        while True:
            data=f.read(BUFF_SIZE)
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

    recv = socket.recv(1025)
    if not recv:
        print("Closed connection")
        exit()
    elif int.from_bytes(recv, byteorder='big') == RETURN_VALUE_FILE_DOESNT_EXIST:
        return None
    else:
        return recv

def getFileFromServer(socket, directoryPath, filepath):
    print("\tUpdating...")
    dataToSend = bytearray()
    dataToSend.append(INSTRUCTION_FILE)
    dataToSend += (filepath.encode("ascii"))
    socket.send(dataToSend)

    fo = open(os.path.join(directoryPath, filepath), "wb")

    data = socket.recv(1025)

    fo.write(data)
    print("\tDone updating")

def checkFilePathForUpdatesAvailable(socket, directoryPath, filepath):
    fileHash = requestFileHash(socket, filepath)
    if fileHash == None:
        if safemode or not updating:
            print(filepath, " \n\tFile does not exist on server. Safemode prevented deletion...")
            return False
        else:
            print(filepath, ": \n\tFile does not exist on server. Removing...")
            os.remove(os.path.join(directoryPath, filepath))
            return False
    elif fileHash == getHashOfFile(os.path.join(directoryPath, filepath)):
        print(filepath, ": \n\tFiles are matching.")
        return False
    else:
        print(filepath, ": \n\tFiles are not matching.")
        return True

def checkForUpdates(directoryPath, address, port):
    relativePathToAllFiles = [os.path.relpath(os.path.join(r, file), directoryPath) for r, s, f in os.walk(directoryPath) for file in f]

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((address, port))

    for filepath in relativePathToAllFiles:
        filepath = filepath.replace(os.path.sep, "/")
        if checkFilePathForUpdatesAvailable(s, directoryPath, filepath):
            if updating:
                getFileFromServer(s, directoryPath, filepath)
            else:
                print("\tUpdate prevented. Do not use the \"-c\" option to update the file.")
    s.close()

# Used for main function
def printHelp():
    print("\nUsage: client.py [-h] [-s] <sourceaddress>:<port> <directory>\n")
    print("Options:")
    print(" -h: \tPrint help.")
    print(" -s: \tSafemode. Files that are not present on the server will not be deleted.")
    print(" -c: \tCheck only. Shows changed files, but prevents updates.")

# Used for mainfunction
def parseOptions():
    for arg in sys.argv[1:]:
        if arg == "-h":
            printHelp()
            exit()
        elif arg == "-s":
            global safemode
            safemode = True
        elif arg == "-c":#
            global updating
            updating = False

# Used for main function
def checkArguments():
    match = re.match(".+:[0-9]+", sys.argv[-2])
    if not match or match.span()[1] != len(sys.argv[-2]):
        printHelp()
        exit()
    if not os.path.exists(sys.argv[-1]):
        print(sys.argv[-1], ": \n\tPath does not exist. Specify a existing path.\n")
        printHelp()
        exit()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        printHelp()
        exit()
    parseOptions()
    checkArguments()
    connectiondata = sys.argv[-2].split(":")
    checkForUpdates(sys.argv[-1], connectiondata[0], int(connectiondata[1]))
