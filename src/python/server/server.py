import socket
import select
from time import sleep
import hashlib
import sys
import os

# arguments: SOURCE_TYPE=<local> REMOTE_SOURCE=<None> BUFFSIZE=<1024> HASH_ALGORITHM=<md5>
# ? VERSIONING=<boolean>, PRECOMPUTE_HASHES=<boolean>

BUF_SIZE = 1024

TIME_OUT = 60   # in seconds

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
            data=f.read(BUF_SIZE)
            print(data)
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

serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

serversocket.bind((socket.gethostname(), 12345))
serversocket.listen(5)

sockets = [serversocket]
socketConnection = dict()



def main():
    while True:
        rdyRead, rdyWrite, inErr = select.select(sockets, sockets, [], TIME_OUT)

        for socket in rdyRead:
            if socket==serversocket:
                (clientSocket, address) = serversocket.accept()
                sockets.append(clientSocket)
                socketConnection[clientSocket] = Connection(clientSocket)
            else:
                if socketConnection[socket].recv():
                    sockets.remove(socket)

        for socket in rdyWrite:
            if socket==serversocket:
                pass
            else:
                socketConnection[socket].send()

if __name__ == "__main__":
    print(sys.argv)
    main()
