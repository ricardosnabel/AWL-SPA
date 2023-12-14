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
DISTANCEX = 262500 / 2
DISTANCEY = 140000 / 2
XMOTORDISTANCE = 92
PIXELSIZE = 9.922
STEPSIZE = 2.5
MAXSTEPS = 1500 # test maximum
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
    time.sleep(1)
    ARDUINO.write(str.encode(str(data)))
    time.sleep(1)
    read_arduino()

def read_arduino():
    while True:
        time.sleep(.5)
        recv = ARDUINO.readline()
        if not recv:
            break
        print(recv)

def convert_um2steps(data):
    if isinstance(data, int) or isinstance(data, float):
        stepsToTake = maxsteps_check(data / STEPSIZE)
    else:
        stepsToTake = []
        for i in data:
            stepsToTake.append(maxsteps_check(i / STEPSIZE))
    return stepsToTake

def convert_pixels2um(data):
    if isinstance(data, int) or isinstance(data, float):
        distInUm = PIXELSIZE * float(data)
    else:
        distInUm = []
        for i in data:
            distInUm.append(PIXELSIZE * float(i))
    return distInUm

def maxsteps_check(steps):
    if steps > MAXSTEPS:
        steps = MAXSTEPS
    elif steps < -MAXSTEPS:
        steps = -MAXSTEPS
    return steps

def move_actuator(data):
    write_to_arduino("start")
    if data[YAXISCAM0] != data[YAXISCAM2]:
        stepsToTake = rotate(data)
        write_to_arduino(stepsToTake)
        write_to_arduino(stepsToTake)
    else:
        stepsToTake = convert_um2steps(convert_pixels2um(data))
        write_to_arduino(stepsToTake[XAXISCAM0])
        write_to_arduino(stepsToTake[YAXISCAM0])
        write_to_arduino(stepsToTake[XAXISCAM2])
    '''stepsToTake = convert_um2steps(convert_pixels2um(data))
    write_to_arduino(stepsToTake[XAXISCAM0])
    write_to_arduino(stepsToTake[YAXISCAM0])
    write_to_arduino(stepsToTake[XAXISCAM2])'''
    write_to_arduino("end")

def rotate(data):
    epsilon = abs(convert_pixels2um(float(data[XAXISCAM0])) - convert_pixels2um(float(data[XAXISCAM2])))
    n = (((XMOTORDISTANCE * XMOTORDISTANCE) / 4) - ((DISTANCEX * DISTANCEX) + (DISTANCEY * DISTANCEY)))
    m = (((DISTANCEY*2) * epsilon) / XMOTORDISTANCE) # * -1
    p = ((epsilon * epsilon) / 4) - (DISTANCEX * DISTANCEX)
    sqrtcalc = (m*m) - (4 * n * p)
    calc = (m + math.sqrt(abs(sqrtcalc))) / (2 * n)
    stepsToTake = convert_um2steps(calc)
    if sqrtcalc < 0:
        stepsToTake = -stepsToTake
    print(calc)
    print(stepsToTake)
    return stepsToTake

def actuators_2neutral():
    write_to_arduino("start")
    write_to_arduino('0')
    write_to_arduino('0')
    write_to_arduino('0')
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
                actuators_2neutral()
                sendmsg(CONNOMRON, MEASURE)
                data = receive_data(CONNOMRON)
                if data[0][0] == 'OK\r':
                    status = 'unaligned'
            case 'unaligned':
                sendmsg(CONNOMRON, MEASURE)
                data = receive_data(CONNOMRON)
                print(data[MEASUREDDATA])
                if data[1] == 'READY\r':
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
                actuators_2neutral()
                status = 'waiting for plate'

def test_program():
    start_time = time.perf_counter()
    sendmsg(CONNOMRON, MEASURE)
    test_data = receive_data(CONNOMRON)
    print(test_data[MEASUREDDATA])

    end_time = time.perf_counter()
    measured_time = end_time - start_time
    print(f'Total runtime: {measured_time:0.4f} seconds')

    move_actuator(test_data[MEASUREDDATA])
    #move_actuator(['200.00', '560.00', '-150.00', '180.00'])
    time.sleep(.5)
    actuators_2neutral()

if __name__ == '__main__':
    #GPIO_init()
    conn_init()
    status = 'waiting for plate'
    try:
        #handle_data(status)
        test_data = receive_data(CONNOMRON)
        while True:
            test_program()
            time.sleep(1)
            '''if runApp == True:
                test_program()
            elif runApp == False:
                print("Program is off.")'''
    except KeyboardInterrupt:
        GPIO.cleanup()
        CONNOMRON.close()
        #CONNEXTERN.close()
        ARDUINO.close()

