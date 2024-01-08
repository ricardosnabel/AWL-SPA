import socket
import re
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
ARDUINO = serial.Serial(port='/dev/ttyUSB0', baudrate=9600, timeout=2)
OMRONCONTROLLER = ['10.5.5.100', 9876]
EXTERNCONTROLLER = ['127.0.0.1', 0]
runApp = False
countSteps = [0, 0, 0] # [Y1, Y2, X]

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
    message = str(data[0]) + ";" + str(data[1]) + ";" + str(data[2]) + ";"
    print("Send Message: ", message)
    ARDUINO.write(str.encode(message))

def read_arduino():
    while True:
        message = ARDUINO.readline()
        print("Received message: ", message)
        return message

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
    YDiff = abs(float(data[YAXISCAM0]) - float(data[YAXISCAM2]))
    if abs(float(data[YAXISCAM0])) > 5.0 or abs(float(data[YAXISCAM2])) > 5.0:
        print("y movement")
        stepsToTake = convert_pixels2steps(data)
        if YDiff > 5:
            print("if ydiff")
            data[YAXISCAM0] = float(data[YAXISCAM0]) * (abs(float(data[YAXISCAM0])) / (abs(float(data[YAXISCAM0])) + abs(float(data[YAXISCAM2]))))
            data[YAXISCAM2] = float(data[YAXISCAM2]) * (abs(float(data[YAXISCAM2])) / (abs(float(data[YAXISCAM0])) + abs(float(data[YAXISCAM2]))))
            stepsToTake = convert_pixels2steps(data)
            stepsToTake[YAXISCAM0] /= 2
            stepsToTake[YAXISCAM2] /= 2
        write = handle_countSteps([stepsToTake[YAXISCAM0], stepsToTake[YAXISCAM2], 0], False, False)
        write_to_arduino(write)
        print("Steps: ", stepsToTake)
    else:
        print("x movement")
        stepsToTake = convert_pixels2steps(data)
        write = handle_countSteps([0, 0, stepsToTake[XAXISCAM0]], False, False)
        write_to_arduino(write)

def to_neutral(steps):
    for i in range(len(steps)):
        if steps[i] >= 0:
            steps[i] = -steps[i]
        else:
            steps[i] = abs(steps[i])
    return steps

def handle_countSteps(steps, clear, getcount):
    global countSteps
    if clear:
        countSteps = [0, 0, 0]
        return 0
    if getcount:
        return countSteps
    else:
        for i in range(len(steps)):
            if abs(countSteps[i] + steps[i]) >= MAXSTEPS:
                steps[i] = 0
            else:
                countSteps[i] += steps[i]
        return steps

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
    firstRun = True
    while True:
        match status:
            case 'waiting for plate':
                handle_countSteps(0, True, False)
                #data = receive_data(CONNEXTERN)
                #if data == 'OK':
                if runApp:
                    firstRun = True
                    print("waiting for plate")
                    status = 'plate arrived'
            case 'plate arrived':
                sendmsg(CONNOMRON, MEASURE)
                data = receive_data(CONNOMRON)
                if data[0][0] == 'OK\r':
                    status = 'unaligned'
            case 'unaligned':
                reading = read_arduino()
                if (reading == b'end\r\n') or firstRun:
                    reading = ""
                    firstRun = False
                    sendmsg(CONNOMRON, MEASURE)
                    data = receive_data(CONNOMRON)
                    print(data)
                    if data[MEASUREDDATA][0] == 'READY\r':
                        status = 'aligned'
                    else:
                        move_actuator(data[MEASUREDDATA])
            case 'aligned':
                sendmsg(CONNEXTERN, 'OK')
                status = 'wait for external module'
            case 'wait for external module':
                if receive_data(CONNEXTERN) == 'OK\r':
                    status = 'return to neutral'
            case 'return to neutral':
                write_to_arduino(to_neutral(handle_countSteps(0, False, True)))
                status = 'waiting for plate'

if __name__ == '__main__':
    #GPIO_init()
    conn_init()
    status = 'plate arrived'
    try:
        #test_data = receive_data(CONNOMRON)
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

