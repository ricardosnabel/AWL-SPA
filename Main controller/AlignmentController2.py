import socket
import time
import serial
import RPi.GPIO as GPIO

'''
How to use the CoVi controller.

Usage of this controller requires Python 3 or higher. To install go to https://www.python.org/downloads/ 
This controller use the pySerial package. If there will be no use of any serial connection, please comment of remove 'import serial' and the functions write_to_serial() and read_serial(). To install this package, follow the instructions in the link in chapter Serial.

Set up a connection:
    Telnet:
    This controller sets a connection between the Omron Vision controller and the CoVi controller. May the IP address of the Omron controller be changed, please change the address in the first element of the 'OMRONCONTROLLER' array. To change the port, use the second element in this array.
    It is also possible to set up an connection with another device, for this it is necessary to insert the IP address of this device in the first element of the 'EXTERNCONTROLLER' array and uncomment all the line using the 'CONNEXTERN' command. To change the port, use the second element in this array.
    To send data, use the sendmsg() function. This function requires the socket of the connection to which the data needs to be transmitted to and the message that will be sent.   
    To receive data, use the receive_data() function. This function requires the socket of the connection from which the data needs to be received.
    For more information, see the documentation of the socket library: https://docs.python.org/3/library/socket.html

    Serial:
    Before using this controller, it is required to install the package pySerial. To install this package, follow the instructions in the link below.
    This controller sets a serial connection between the Actuator controller and the CoVi controller. Before using this controller, check and/or change the port on which the Actuator controller is connected to in the variable SERIAL.
    To send data, use the write_to_serial() function. This function requires the message that will be sent to the Actuator controller.
    To receive data, use the read_serial() function.
    For more information, see the documentation of the pySerial library: https://pyserial.readthedocs.io/en/latest/pyserial.html

Omron controller:
To measure, send the message in the variable 'MEASURE' using the function sendmsg(). To change the layout of the Omron, send the message in the variable 'LAYOUT' using the function sendmsg(). To change the layout, change the second number in the variable 'LAYOUT' to the required layout.
Data from the Omron controller will be stored in an array. The first element of this array contains the execution message in the form of an 'OK\r' (may the command be executed succesfully) or 'ERR\r' (may an error occured while executing the command), the second element contains the data from the Omron controller in the form of an 'READY\r' (the plate has been aligned succesfully) or a array containing the measurement values (example: [XAXISCAM0, YAXISCAM0, XAXISCAM2, YAXISCAM2]).

Manipulating the data:
Received data will be in pixels, check the camera settings and calculate the size per pixel in micrometers. Replace the amount in the variable 'PIXELSIZE'.
When data is received, this will be converted from pixels to steps. To remain the right calculations, check the distance the actuator moves when taking a single step. Replace the distance per step in the variable 'STEPSIZE'.
To ensure the safety of the compliant mechanism, the controller checks if the amount of steps is not greater than the steps stored in the variable 'MAXSTEPS'.

Start and stop the controller:
To be used in production, the controller will start when it receives a message from an external device. Before using this controller, change the variable 'EXTERNRECV' to the expected message the controller will receive. In the state 'waiting for plate' in function run_covi() replace the line 'if runApp:' with the following two lines: 'data = receive_data(CONNEXTERN)' and 'if data[0] == EXTERNRECV:'.
The CoVi controller is equipped with two buttons, red and green, to be used without receiving a message from an external device. Therefore, in the state 'waiting for plate' in function run_covi(), replace the following two lines 'data = receive_data(CONNEXTERN)' and 'if data[0] == EXTERNRECV:' with the following: 'if runApp':
These buttons are used to start the controller when this is not used in production.
Pushing the green button interrupts the controller and will run the function run_covi(). While running, the LED is turned on.
Pushing the red button interrupts the controller and will stop the function run_covi(). The LED will turn off.

'''

MEASUREDDATA = 1                                                            # Index for the measurement data received from the Omron controller
XAXISCAM0 = 0                                                               # Index for the measurement value of the X axis on camera 0
YAXISCAM0 = 1                                                               # Index for the measurement value of the Y axis on camera 0
XAXISCAM2 = 2                                                               # Index for the measurement value of the X axis on camera 2
YAXISCAM2 = 3                                                               # Index for the measurement value of the Y axis on camera 2
EXTERNRECV = 'OK\r'                                                         # Message to receive to run the controller
MEASURE = 'M'                                                               # Command to run a measurement on the Omron controller
LAYOUT = 'DLN 0 1'                                                          # Set layout command for the Omron controller 
PIXELSIZE = 9.922                                                           # Size of a single pixel in micrometers
STEPSIZE = .625                                                             # Single step distance in micrometers
MAXSTEPS = 7500                                                             # Maximum steps to set for all directions.
LED = 11                                                                    # GPIO pin for the LED
REDBUTTON = 16                                                              # GPIO pin for the red button
GREENBUTTON = 15                                                            # GPIO pin for the green button
CONNOMRON = socket.socket(socket.AF_INET, socket.SOCK_STREAM)               # Create a socket for the connection with the Omron controller
CONNEXTERN = socket.socket(socket.AF_INET, socket.SOCK_STREAM)              # Create a socket for the connection with an external device
SERIAL = serial.Serial(port='/dev/ttyUSB0', baudrate=2000000, timeout=.1)   # Creates a serial connection
OMRONCONTROLLER = ['10.5.5.100', 9876]                                      # Sets the IP address and port of the Omron controller
EXTERNCONTROLLER = ['127.0.0.1', 0]                                         # Sets the IP address and port of an external device
runApp = False                                                              # Boolean variable to start (true) and stop (false) the controller

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
    GPIO.add_event_detect(REDBUTTON, GPIO.RISING, callback=handle_buttonINT, bouncetime=1000)       # handle_redbutton
    GPIO.add_event_detect(GREENBUTTON, GPIO.RISING, callback=handle_buttonINT, bouncetime=1000)     # handle_greenbutton

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
    write_to_serial("start")
    YDiff = abs(float(data[YAXISCAM0]) - float(data[YAXISCAM2]))
    stepsToTake = convert_pixels2steps(data)
    if abs(float(data[YAXISCAM0])) > 2.5 or abs(float(data[YAXISCAM2])) > 2.5:
        if YDiff > 4:
            data[YAXISCAM0] = float(data[YAXISCAM0]) * (abs(float(data[YAXISCAM0])) / (abs(float(data[YAXISCAM0])) + abs(float(data[YAXISCAM2]))))
            data[YAXISCAM2] = float(data[YAXISCAM2]) * (abs(float(data[YAXISCAM2])) / (abs(float(data[YAXISCAM0])) + abs(float(data[YAXISCAM2]))))
            print(data[YAXISCAM2])
            print(data[YAXISCAM0])
            stepsToTake = convert_pixels2steps(data)
            stepsToTake[YAXISCAM0] /= 1.92
            stepsToTake[YAXISCAM2] /= 1.92
        write_to_serial(stepsToTake[YAXISCAM0])
        write_to_serial(stepsToTake[YAXISCAM2])
        print("Steps: ", stepsToTake)
    else:
        write_to_serial(0)
        write_to_serial(0)
        write_to_serial(stepsToTake[XAXISCAM0])
    write_to_serial("end")

def handle_buttonINT(channel):
    global runApp
    if channel == REDBUTTON:
        runApp = False
        print("red")
        GPIO.output(11, 0)
    elif channel == GREENBUTTON:
        runApp = True
        print("green")
        GPIO.output(11, 1)

def handle_greenbutton(channel):
    global runApp
    runApp = True
    print("green")
    GPIO.output(11, 1)

def handle_redbutton(channel):
    global runApp
    runApp = False
    print("red")
    GPIO.output(11, 0)

def run_covi(status):
    while True:
        while runApp:
            match status:
                case 'waiting for plate':
                    #if runApp:
                    status = 'plate arrived'
                case 'plate arrived':
                    sendmsg(CONNOMRON, MEASURE)
                    data = receive_data(CONNOMRON)
                    if data[0][0] == 'OK\r' and data[MEASUREDDATA][0] is not 'OK':
                        status = 'unaligned'
                case 'unaligned':
                    sendmsg(CONNOMRON, MEASURE)
                    data = receive_data(CONNOMRON)
                    print(data[MEASUREDDATA])
                    if data[1][0] == 'OK':
                        status = 'aligned'
                    else:
                        move_actuator(data[MEASUREDDATA])
                case 'aligned':
                    #sendmsg(CONNEXTERN, 'OK')
                    status = 'wait for external module'
                case 'wait for external module':
                    #if receive_data(CONNEXTERN) == 'OK\r':
                    status = 'return to neutral'
                case 'return to neutral':
                    status = 'waiting for plate'

if __name__ == '__main__':
    GPIO_init()
    conn_init()
    status = 'waiting for plate'
    try:
        run_covi(status)
    except KeyboardInterrupt:
        GPIO.cleanup()
        CONNOMRON.close()
        #CONNEXTERN.close()
        SERIAL.close()
    GPIO.cleanup()