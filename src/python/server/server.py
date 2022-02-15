import socket
import select
import hashlib
import sys
import os
import re

# config

BUFF_SIZE = 1024
HASH_ALGORITHM = "md5"
PRECOMPUTE_HASHES = False
VERSIONS = False

TIME_OUT = 60   # in seconds

# instruction and state constants

RECV = 0
SEND = 1

INSTRUCTION_CLOSE = 0
INSTRUCTION_HASH = 1
INSTRUCTION_FILE = 2

RETURN_VALUE_FILE_DOESNT_EXIST = 8

def getFileAsByteArray(filename):
    fo = open("./source/"+filename, "rb")
    return fo.read()

def getHashOfFile(filename):
    md5 = hashlib.md5()
    with open("./source/"+filename, 'rb') as f:
        while True:
            data=f.read(BUFF_SIZE)
            if not data:
                break
            md5.update(data)
    return md5.digest()

class Connection:

    def __init__(self, socket):
        self.socket = socket
        self.state = RECV
        self.data = None
        self.instruction = None

    def send(self):
        if self.state == RECV:
            return
        m_bytes = bytearray()
        if self.instruction == INSTRUCTION_HASH:
            if os.path.exists("./source/"+self.data):
                m_bytes += getHashOfFile(self.data)
            else:
                m_bytes.append(RETURN_VALUE_FILE_DOESNT_EXIST)
        elif self.instruction == INSTRUCTION_FILE:
             m_bytes += getFileAsByteArray(self.data)
        self.socket.send(m_bytes)
        self.state = RECV

    def recv(self):
        if self.state != RECV:
            return
        data = self.socket.recv(1024)
        if not data or data[0] == INSTRUCTION_CLOSE:
            self.socket.close()
            return True
        self.data = data[1:].decode('ascii')
        if data[0] == INSTRUCTION_FILE or data[0] == INSTRUCTION_HASH:
            self.instruction = data[0]
            self.state = SEND
        return False

def openConfigFile(configFilePath):
    if configFilePath != None:
        if not os.path.exists(configFilePath):
            print("No config file found at the specified location. Trying to use default config file...")
        else:
            return open(configFilePath, 'r')
    if not os.path.exists("config.txt"):
        return None
    else:
        return open("config.txt", 'r')

def parseConfigLine(line):
    parts = line.split(":")
    if parts[0] == "BUFF_SIZE":
        if not re.match("\"[0-9]+\"", parts[1]):
            print("\"BUFF_SIZE\" has to be an integer representing the amount of bytes processed at the same time.")
            return
        global BUFF_SIZE
        BUFF_SIZE = int(parts[1][1:-1])
    elif parts[0] == "HASH_ALGORITHM":
        global HASH_ALGORITHM
        if parts[1] == "\"md5\"":
            HASH_ALGORITHM = "md5"
        elif parts[1] == "\"sha256\"":
            HASH_ALGORITHM = "sha256"
        else:
            print("Unsupported hash algorithm. Ignoring...")
    elif parts[0] == "VERSIONS":
        global VERSIONS
        if parts[1] == "\"enabled\"":
            VERSIONS = True
        elif parts[1] == "\"disabled\"":
            VERSIONS = False
        else:
            print("Ignoring...  Use \"enabled\" or \"disabled\".")
    elif parts[0] == "PRECOMPUTE_HASHES":
        global PRECOMPUTE_HASHES
        if parts[1] == "\"enabled\"":
            PRECOMPUTE_HASHES = True
        elif parts[1] == "\"disabled\"":
            PRECOMPUTE_HASHES = False
        else:
            print("Ignoring...  Use \"enabled\" or \"disabled\".")
    elif parts[0] == "TIME_OUT":
        if not re.match("\"[0-9]+\"", parts[1]):
            print("\"TIME_OUT\" has to be an integer representing the number of seconds the select statement waits.")
            return
        global TIME_OUT
        TIME_OUT = int(parts[1][1:-1])
    else:
        print("Ignoring line, unknown option.")

def readAndParseConfigFile(configFilePath):
    file = openConfigFile(configFilePath)
    if file == None:
        print("No config file found. Using default values...")
        return
    pattern = re.compile("[A-Z_]+:\"[0-9a-zA-Z]+\"")
    for line in file.read().split("\n"):
        if len(line) == 0:
            continue
        match = pattern.match(line)
        if match and match.span()[1] == len(line):
            parseConfigLine(line)
        else:
            print("Ignoring line: ", line)

def initalizeServer():
    global serversocket
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    serversocket.bind((socket.gethostname(), 12345))
    serversocket.listen(5)

    global sockets
    sockets = [serversocket]
    global socketConnection
    socketConnection = dict()

def serverLoop():
    while True:
        rdyRead, rdyWrite, inErr = select.select(sockets, sockets, [], TIME_OUT)

        for s in rdyRead:
            if s==serversocket:
                (clientSocket, address) = serversocket.accept()
                sockets.append(clientSocket)
                socketConnection[clientSocket] = Connection(clientSocket)
            else:
                if socketConnection[s].recv():
                    sockets.remove(s)

        for s in rdyWrite:
            if s==serversocket:
                pass
            else:
                socketConnection[s].send()

if __name__ == "__main__":
    readAndParseConfigFile(sys.argv[1] if len(sys.argv) == 2 else None)
    initalizeServer()
    serverLoop()
