import socket
import time
import serial
import RPi.GPIO as GPIO

measuredData = 1
XAxisCam0 = 0
YAxisCam0 = 1
XAxisCam2 = 2
YAxisCam2 = 3
measure = 'M'
pixelSize = 9.922
stepSize = 2.5
maxSteps = 1900
led = 11
redButton = 13
greenButton = 15
status = 'waiting for plate'
runApp = False

def conn_init():
    global connOmron, connExtern, arduino
    connOmron = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connExtern = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    arduino = serial.Serial(port='/dev/ttyUSB0', baudrate=2000000, timeout=.1)
    
    omronController = ['10.5.5.100', 9876]
    externController = ['127.0.0.1', 0]
    
    connOmron.connect((omronController[0], omronController[1]))
    #connExtern.connect((externController[0], externController[1]))

def GPIO_init():
    GPIO.setmode(GPIO.BOARD)
    
    GPIO.setup(led, GPIO.OUT)
    GPIO.setup(redButton, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(greenButton, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    GPIO.add_event_detect(redButton,GPIO.RISING,callback=handle_redbutton)
    GPIO.add_event_detect(greenButton,GPIO.RISING,callback=handle_greenbutton)

def telnet_connection(sock, host, port):
    try:
        sock.settimeout(1)
        sock.connect((host, port))
        return True
    except:
        return False

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
    arduino.write(str.encode(str(data)))
    time.sleep(1)
    read_arduino()

def read_arduino():
    while True:
        time.sleep(.5)
        recv = arduino.readline()
        if not recv:
            break
        print(recv)

def convert_pixels2steps(data):
    stepsToTake = []
    for i in data:
        calc = pixelSize * float(i) / stepSize
        if calc > maxSteps:
            calc = maxSteps
        stepsToTake.append(calc)
    return stepsToTake

def move_actuator(data):
    stepsToTake = convert_pixels2steps(data)
    write_to_arduino("start")
    if data[YAxisCam0] != data[YAxisCam2]:
        write_to_arduino(stepsToTake[YAxisCam0])
        write_to_arduino(stepsToTake[YAxisCam2])
    else:
        write_to_arduino(stepsToTake[XAxisCam0])
        write_to_arduino(stepsToTake[YAxisCam0])
        write_to_arduino(stepsToTake[XAxisCam2])
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
    global runApp, status
    runApp = True
    status = 'plate arrived'
    GPIO.output(11, 1)

    GPIO.remove_event_detect(greenButton)
    time.sleep(1)
    GPIO.add_event_detect(greenButton,GPIO.RISING,callback=handle_greenbutton)

def handle_redbutton(channel):
    global runApp, status
    runApp = False
    status = 'return to neutral'
    GPIO.output(11, 0)

    GPIO.remove_event_detect(redButton)
    time.sleep(1)
    GPIO.add_event_detect(redButton,GPIO.RISING,callback=handle_redbutton)

def handle_data(status):
    match status:
        case 'waiting for plate':
            data = receive_data(connExtern)
            if data == 'OK':
                status = 'plate arrived'
        case 'plate arrived':
            actuators_2neutral()
            sendmsg(connOmron, measure)
            data = receive_data(connOmron)
            if data[0] == 'OK':
                status = 'unaligned'
        case 'unaligned':
            sendmsg(connOmron, measure)
            data = receive_data(connOmron)
            if data[1] == 'READY':
                status = 'aligned'
            else:
                move_actuator(data[1])
        case 'aligned':
            sendmsg(connExtern, 'OK')
            status = 'wait for external module'
        case 'wait for external module':
            if receive_data(connExtern) == 'OK':
                status = 'return to neutral'
        case 'return to neutral':
            actuators_2neutral()
            status = 'waiting for plate'

def test_program():   
    start_time = time.perf_counter()
    sendmsg(connOmron, measure)
    test_data = receive_data(connOmron)
    print(test_data[measuredData])

    end_time = time.perf_counter()
    measured_time = end_time - start_time
    print(f'Total runtime: {measured_time:0.4f} seconds')

    move_actuator(test_data[measuredData])
    time.sleep(2)
    actuators_2neutral()

if __name__ == '__main__':
    GPIO_init()
    conn_init()

    try:
        while True:
            time.sleep(1)
            if runApp == True:
                test_program()
            elif runApp == False:
                print("Program is off.")
    except KeyboardInterrupt:
        GPIO.cleanup()
        connOmron.close()
        #connExtern.close()
        arduino.close()
    
