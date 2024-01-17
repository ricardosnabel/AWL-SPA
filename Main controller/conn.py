import socket
import serial
import time

MEASURE = 'M'                                                               # Command to run a measurement on the Omron controller
LAYOUT = 'DLN 0 1'                                                          # Set layout command for the Omron controller 
CONNOMRON = socket.socket(socket.AF_INET, socket.SOCK_STREAM)               # Create a socket for the connection with the Omron controller
CONNTRANSPORT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)           # Create a socket for the connection with an external device
CONNSCREENPRINT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)         # Create a socket for the connection with an external device
SERIAL = serial.Serial(port='/dev/ttyUSB0', baudrate=2000000, timeout=.1)   # Creates a serial connection
OMRONCONTROLLER = ['10.5.5.100', 9876]                                      # Sets the IP address and port of the Omron controller
TRANSPORT = ['127.0.0.1', 0]                                                # Sets the IP address and port of an external device
SCREENPRINT = ['127.0.0.1', 0]                                              # Sets the IP address and port of an external device

def conn_init():
    CONNOMRON.settimeout(1)
    CONNOMRON.connect((OMRONCONTROLLER[0], OMRONCONTROLLER[1]))
    sendmsg(CONNOMRON, LAYOUT)
    measure()
    #CONNTRANSPORT.settimeout(1)
    #CONNTRANSPORT.connect((TRANSPORT[0], TRANSPORT[1]))
    #CONNSCREENPRINT.settimeout(1)
    #CONNSCREENPRINT.connect((SCREENPRINT[0], SCREENPRINT[1]))

def conn_close():
    CONNOMRON.close()
    #CONNTRANSPORT.close()
    #CONNSCREENPRINT.close()
    SERIAL.close()

def sendmsg(sock, message):
    sock.send(message.encode())

def receive_data(sock):
    fragments = []
    while True:
        try:
            data = sock.recv(1024)
            print(data)
            fragments.append(data
                             .decode()
                             .replace(" ", "")
                             .split(","))
        except TimeoutError:
            return fragments

def write_to_serial(data):
    time.sleep(2)
    SERIAL.write(str.encode(str(data)))
    time.sleep(2)

def read_serial():
    while True:
        time.sleep(.5)
        recv = SERIAL.readline()
        if not recv:
            break
        print(recv)

def measure():
    sendmsg(CONNOMRON, MEASURE)
    time.sleep(2)

def aligned():
    sendmsg(CONNSCREENPRINT, 'OK')

def omron_recv():
    return receive_data(CONNOMRON)

def transport_recv():
    return receive_data(CONNTRANSPORT)

def screenprint_recv():
    return receive_data(CONNSCREENPRINT)
