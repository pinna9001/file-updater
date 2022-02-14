import socket
import hashlib
import os
import sys

BUF_SIZE = 1024

INSTRUCTION_CLOSE = 0
INSTRUCTION_HASH = 1
INSTRUCTION_FILE = 2

RETURN_VALUE_FILE_DOESNT_EXIST = 8

filename = "file3.txt"

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

def main(directoryPath):
    print("main")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("localhost", 12345))
    fileHash = requestFileHash(s, filename)

    if fileHash == None:
        print("file doesn't exist on server. File will be deleted.")
        os.remove("F:/file-updater/src/python/client/"+filename)
    elif fileHash == getHashOfFile("F:/file-updater/src/python/client/"+filename):
        print("Current files are matching. Nothing will be updated.")
    else:
        print("Current files are not matching. The existing file will be updated.")

        dataToSend = bytearray()
        dataToSend.append(INSTRUCTION_FILE)
        dataToSend += ("file3.txt".encode("ascii"))
        s.send(dataToSend)

        data = s.recv(1024)

        fo = open("F:/file-updater/src/python/client/"+filename, "wb")

        fo.write(data)

    s.close()

if __name__ == "__main__":
    print(sys.argv)
    main(".")
