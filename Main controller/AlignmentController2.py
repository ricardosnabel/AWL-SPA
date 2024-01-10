import socket
import time
import math
import serial
import RPi.GPIO as GPIO

MEASUREDDATA = 1
XAXISCAM0 = 0
YAXISCAM0 = 1
XAXISCAM2 = 2
YAXISCAM2 = 3
MEASURE = 'M'
LAYOUT = 'DLN 0 1'
PIXELSIZE = 9.922
STEPSIZE = .625
MAXSTEPS = 7500 # test maximum
LED = 11
REDBUTTON = 16
GREENBUTTON = 15
CONNOMRON = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
CONNEXTERN = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ARDUINO = serial.Serial(port='/dev/ttyUSB0', baudrate=2000000, timeout=.1)
OMRONCONTROLLER = ['10.5.5.100', 9876]
EXTERNCONTROLLER = ['127.0.0.1', 0]
runApp = False

def conn_init():
    CONNOMRON.settimeout(1)
    CONNOMRON.connect((OMRONCONTROLLER[0], OMRONCONTROLLER[1]))
    sendmsg(CONNOMRON, LAYOUT)
    #CONNEXTERN.settimeout(1)
    #CONNEXTERN.connect((EXTERNCONTROLLER[0], EXTERNCONTROLLER[1]))

def GPIO_init():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(LED, GPIO.OUT)
    GPIO.setup(REDBUTTON, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(GREENBUTTON, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.add_event_detect(REDBUTTON,GPIO.RISING,callback=handle_redbutton)
    GPIO.add_event_detect(GREENBUTTON,GPIO.RISING,callback=handle_greenbutton)

def sendmsg(sock, message):
    sock.send(message.encode())

def receive_data(sock):
    fragments = []
    while True:
        try:
            data = sock.recv(1024)
            fragments.append(data.decode().replace(" ", "").split(","))
        except TimeoutError:
            return fragments

def write_to_arduino(data):
    time.sleep(2)
    ARDUINO.write(str.encode(str(data)))
    time.sleep(2)

def read_arduino():
    while True:
        time.sleep(.5)
        recv = ARDUINO.readline()
        if not recv:
            break
        print(recv)

def convert_pixels2steps(data):
    if isinstance(data, float):
        distInUm = PIXELSIZE * data
        stepsToTake = maxsteps_check(distInUm / STEPSIZE)
    else:
        stepsToTake = []
        for i in data:
            distInUm = PIXELSIZE * float(i)
            stepsToTake.append(maxsteps_check(distInUm / STEPSIZE))
    print("StepsToTake: ", stepsToTake)
    return stepsToTake

def maxsteps_check(steps):
    if steps > MAXSTEPS:
        steps = MAXSTEPS
    elif steps < -MAXSTEPS:
        steps = -MAXSTEPS
    return steps

def move_actuator(data):
    write_to_arduino("start")
    YDiff = abs(float(data[YAXISCAM0]) - float(data[YAXISCAM2]))
    if abs(float(data[YAXISCAM0])) > 5.0 or abs(float(data[YAXISCAM2])) > 5.0:
        stepsToTake = convert_pixels2steps(data)
        if YDiff > 5:
            data[YAXISCAM0] = float(data[YAXISCAM0]) * (abs(float(data[YAXISCAM0])) / (abs(float(data[YAXISCAM0])) + abs(float(data[YAXISCAM2]))))
            data[YAXISCAM2] = float(data[YAXISCAM2]) * (abs(float(data[YAXISCAM2])) / (abs(float(data[YAXISCAM0])) + abs(float(data[YAXISCAM2]))))
            print(data[YAXISCAM2])
            print(data[YAXISCAM0])
            stepsToTake = convert_pixels2steps(data)
            stepsToTake[YAXISCAM0] /= math.sqrt(4)
            stepsToTake[YAXISCAM2] /= math.sqrt(4)
        write_to_arduino(stepsToTake[YAXISCAM0])
        write_to_arduino(stepsToTake[YAXISCAM2])
        print("Steps: ", stepsToTake)
    else:
        stepsToTake = convert_pixels2steps(data)
        write_to_arduino(0)
        write_to_arduino(0)
        write_to_arduino(stepsToTake[XAXISCAM0])
    write_to_arduino("end")

def handle_greenbutton(channel):
    global runApp
    runApp = True
    print("green")
    GPIO.output(11, 1)
    GPIO.remove_event_detect(GREENBUTTON)
    time.sleep(1)
    GPIO.add_event_detect(GREENBUTTON,GPIO.RISING,callback=handle_greenbutton)

def handle_redbutton(channel):
    global runApp
    runApp = False
    print("red")
    GPIO.output(11, 0)
    GPIO.remove_event_detect(REDBUTTON)
    time.sleep(1)
    GPIO.add_event_detect(REDBUTTON,GPIO.RISING,callback=handle_redbutton)

def handle_data(status):
    while True:
        match status:
            case 'waiting for plate':
                #data = receive_data(CONNEXTERN)
                #if data == 'OK':
                if runApp:
                    print("waiting for plate")
                    status = 'plate arrived'
            case 'plate arrived':
                sendmsg(CONNOMRON, MEASURE)
                data = receive_data(CONNOMRON)
                if data[0][0] == 'OK\r':
                    status = 'unaligned'
            case 'unaligned':
                sendmsg(CONNOMRON, MEASURE)
                data = receive_data(CONNOMRON)
                print(data[MEASUREDDATA])
                if data[1][0] == 'READY\r':
                    status = 'aligned'
                else:
                    #time.sleep(5)
                    move_actuator(data[MEASUREDDATA])
            case 'aligned':
                sendmsg(CONNEXTERN, 'OK')
                status = 'wait for external module'
            case 'wait for external module':
                if receive_data(CONNEXTERN) == 'OK\r':
                    status = 'return to neutral'
            case 'return to neutral':
                status = 'waiting for plate'

if __name__ == '__main__':
    #GPIO_init()
    conn_init()
    status = 'plate arrived'
    try:
        test_data = receive_data(CONNOMRON)
        handle_data(status)
        '''while True:
            test_program()
            handle_data(status)
            time.sleep(1)
            if runApp == True:
                test_program()
            elif runApp == False:
                print("Program is off.")'''
    except KeyboardInterrupt:
        GPIO.cleanup()
        CONNOMRON.close()
        #CONNEXTERN.close()
        ARDUINO.close()