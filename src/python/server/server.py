import socket
import select
from time import sleep
import hashlib

# arguments: buffsize to send, source, hashalgorithm

BUF_SIZE = 1024

RECV = 0
SEND = 1

INSTRUCTION_CLOSE = 0
INSTRUCTION_HASH = 1
INSTRUCTION_FILE = 2

def getFileAsByteArray(filename):
    fo = open("G:\\updater\\server\\"+filename, "rb")
    return fo.read()

def getHashOfFile(filename):
    md5 = hashlib.md5()
    with open("G:\\updater\\server\\"+filename, 'rb') as f:
        while True:
            data=f.read(BUF_SIZE)
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
            m_bytes += getHashOfFile(self.data)
        elif self.instruction == INSTRUCTION_FILE:
             m_bytes += getFileAsByteArray(self.data)
        socket.send(m_bytes)
        self.state = RECV
        
    def recv(self):
        if self.state != RECV:
            return
        data = socket.recv(1024)
        if not data or data[0] == INSTRUCTION_CLOSE:
            socket.close()
            return True
        self.data = data[1:].decode('ascii')
        if data[0] == INSTRUCTION_FILE or data[0] == INSTRUCTION_HASH:
            self.instruction = data[0]
            self.state = SEND
        return False

serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

serversocket.bind(("localhost", 12345))
serversocket.listen(5)

sockets = [serversocket]
socketConnection = dict()

while True:
    rdyRead, rdyWrite, inErr = select.select(sockets, sockets, [])
    
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