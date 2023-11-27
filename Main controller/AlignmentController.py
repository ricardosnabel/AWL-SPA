import socket
import time
import serial

measuredData = 1
XAxisCam0 = 0
YAxisCam0 = 1
XAxisCam2 = 2
YAxisCam2 = 3
connOmron = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connExtern = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
arduino = serial.Serial(port='/dev/ttyUSB0', baudrate=2000000, timeout=.1)
omronController = ['10.5.5.100', 9876]
externController = ['127.0.0.1', 0]
measure = 'M'
pixelSize = 9.922
stepSize = 2.5
#status = 'waiting for plate'
status = 'plate arrived'

def handle_data(status):
    match status:
        case 'waiting for plate':
            #if telnet_connection(externController[0], externController[1]):
            data = receive_data(connExtern)
            if data == 'OK':
                status = 'plate arrived'
        case 'plate arrived':
            sendmsg(connOmron, measure)
            data = receive_data(connOmron)
            if data[0] == 'OK':
                status = 'unaligned'
        case 'unaligned':
            sendmsg(connOmron, measure)
            data = receive_data(connOmroln)
            if data[1] == 'READY':
                status = 'aligned'
            else:
                stepsToTake = convert_pixels2steps(data[1])
                if not arduino.is_open:
                    arduino = connect_to_arduino()
                    print("is_open if werkt")
                write_to_arduino(stepsToTake)
        case 'aligned':
            sendmsg(connExtern, 'OK')
            status = 'return to neutral'
        case 'return to neutral':
            if receive_data(connExtern) == 'OK':
                write_to_arduino('0')
                arduino.close()
                status = 'waiting for plate'

def convert_pixels2steps(pixels):
    pixels = float(pixels)
    pixelsInMicro = pixelSize * abs(pixels)
    stepsToTake = pixelsInMicro / stepSize
    return stepsToTake

def receive_data(sock):
    fragments = []
    while True:
        try:
            data = sock.recv(1024)
            fragments.append(data.decode().replace(" ", "").split(","))
        except TimeoutError:
            return fragments

def connect_to_arduino():
    arduino = serial.Serial(port='/dev/ttyUSB0', baudrate=2000000, timeout=.1)
    return arduino

def write_to_arduino(data):
    time.sleep(.5)
    arduino.write(str.encode(str(data)))
    time.sleep(.5)
    while True:
        time.sleep(2)
        recv = arduino.readline()
        if not recv:
            break
        print(recv)

def telnet_connection(sock, host, port):
    try:
        sock.settimeout(1)
        sock.connect((host, port))       
        return True
    except:
        return False

def sendmsg(sock, message):
    sock.send(message.encode())

def move_actuator(axis, data):
    print("joe")
    stepsToTakeX = convert_pixels2steps(data[XAxisCam0])
    stepsToTakeY = convert_pixels2steps(data[YAxisCam0])
    writeData = stepsToTakeY
    write_to_arduino(writeData)
    writeData = stepsToTakeX
    write_to_arduino(writeData)
        # rotate plate
        #rotate(data)

def rotate(data):
    return 0

def test_program():
    #if not telnet_connection(connOmron, omronController[0], omronController[1]):
    #    print("Connection error.")
    #    return 0
    
    start_time = time.perf_counter()
    
    #sendmsg(connOmron, measure)
    #test_data = receive_data(connOmron)
    test_data = ['623.0000', '-1359.0000', '-249.0000', '-1263.0000\r']
    print(test_data)

    end_time = time.perf_counter()
    measured_time = end_time - start_time
    print(f'Total runtime: {measured_time:0.4f} seconds')

    #stepsToTake = convert_pixels2steps(test_data[measuredData][1])

    #write_to_arduino(abs(stepsToTake))
    move_actuator(0, test_data)
    #write_to_arduino(['Y', ['0', '600'], 'X', ['0', '600']])
    #write_to_arduino(['Y', ['0', '0'], 'X', ['0', '0']])

test_program()
arduino.close()
connOmron.close()
