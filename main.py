# will hear 11235/UDP for any symbols and send random integers to 11234/UDP

import random
import sys
import time
import socket
import errno

# GENERIC params
UPDATE_FREQ = 0.1               # net buffer check frequency

# LISTEN socket defines
LSOCK_PORT = 11235              # listen port
LSOCK_ADDR = "localhost"        # listen addr
LSOCK_RBYTES = 1024             # listen buffer

# SEND socket defines
SSOCK_PORT = 11234              # send port
SSOCK_ADDR = "localhost"        # send addr

def networkReceive():
    """
    Coroutine for receiving datagrams
    :return: str
    """
    while True:
        try:
            sReceive = sockListenSocket.recv(LSOCK_RBYTES)
        except socket.error as sockError:
            sockErrType = sockError.args[0]
            if ((sockErrType == errno.EAGAIN) or (sockErrType == errno.EWOULDBLOCK)):
                yield ""
                continue
            else:
                sys.stdout.write(sockError)
                exit(-1)
        else:
            yield sReceive.decode('utf-8')

def networkSender(socket, sSendAddr, iSendPort):
    """
    Coroutine for sending random integer as UDP datagram
    :param socket: initialized socket
    :param sSendAddr: str, address to send
    :param iSendPort: int, port to send
    :return: none
    """
    while True:
        iInteger = random.randrange(-sys.maxsize, sys.maxsize)
        socket.sendto(str(iInteger).encode("utf-8"), (sSendAddr, iSendPort))
        yield

# set listen socket
sockListenSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sockListenSocket.setblocking(0)
sockListenSocket.bind((LSOCK_ADDR, LSOCK_PORT))

# set send socket
sockSendSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sockSendSocket.setblocking(0)

# init coroutines
networkReader = networkReceive()
networkWriter = networkSender(sockSendSocket, SSOCK_ADDR, SSOCK_PORT)

# main
try:
    while True:
        sys.stdout.write(next(networkReader))
        next(networkWriter)
        sys.stdout.flush()
        time.sleep(UPDATE_FREQ)
except KeyboardInterrupt:
    sys.stdout.write("Exit, closing sockets... ")
    sockSendSocket.close()
    sockListenSocket.close()
    exit(0)