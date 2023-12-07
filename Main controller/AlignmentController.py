import socket
import time
import serial
import RPi.GPIO as GPIO

MEASUREDDATA = 1
XAXISCAM0 = 0
YAXISCAM0 = 1
XAXISCAM2 = 2
YAXISCAM2 = 3
MEASURE = 'M'
PIXELSIZE = 9.922
STEPSIZE = 2.5
MAXSTEPS = 1900
LED = 11
REDBUTTON = 13
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

def convert_pixels2steps(data):
    stepsToTake = []
    for i in data:
        calc = PIXELSIZE * float(i) / STEPSIZE
        if calc > MAXSTEPS:
            calc = MAXSTEPS
        stepsToTake.append(calc)
    return stepsToTake

def move_actuator(data):
    stepsToTake = convert_pixels2steps(data)
    write_to_arduino("start")
    if data[YAXISCAM0] != data[YAXISCAM2]:
        write_to_arduino(stepsToTake[YAXISCAM0])
        write_to_arduino(stepsToTake[YAXISCAM2])
    else:
        write_to_arduino(stepsToTake[XAXISCAM0])
        write_to_arduino(stepsToTake[YAXISCAM0])
        write_to_arduino(stepsToTake[XAXISCAM2])
    write_to_arduino("end")

def rotate(data):
    return 0

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
    time.sleep(2)
    actuators_2neutral()

if __name__ == '__main__':
    GPIO_init()
    conn_init()
    status = 'waiting for plate'
    try:
        handle_data(status)
        '''while True:
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
    
