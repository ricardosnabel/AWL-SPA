How to use the CoVi controller.

Usage of this controller requires Python 3 or higher. To install go to https://www.python.org/downloads/ 
This controller use the pySerial package. If there will be no use of any serial connection, please comment or remove 'import serial' and the functions write_to_serial() and read_serial(). To install this package, follow the instructions in the link in chapter Serial.

Set up a connection:
    Telnet:
    This controller sets a connection between the Omron Vision controller and the CoVi controller. May the IP address of the Omron controller be changed, please change the address in the first element of the 'OMRONCONTROLLER' array. To change the port, use the second element in this array.
    It is also possible to set up an connection with the transport system and screen printing module, therefore it is necessary to insert the IP addresses in the first element of the 'TRANSPORT' and 'SCREENPRINT' array and uncomment all the lines using the 'CONNTRANSPORT' and 'CONNSCREENPRINT' command. To change the port, use the second element in these arrays.
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
To be used in production, the controller will start when it receives a message from the transport system. Before using this controller, change the variable 'TRANSPORTRECV' to the expected message the controller will receive. In the state 'waiting for plate' in function run_covi() uncomment the following two lines: 'transportdata = receive_data(CONNTRANSPORT)' and 'if transportdata[0] == TRANSPORTRECV:'.
The CoVi controller is equipped with two buttons, red and green, to be used without receiving a message from an external device. Therefore, in the state 'waiting for plate' in function run_covi(), make sure the following two lines 'transportdata = receive_data(CONNTRANSPORT)' and 'if transportdata[0] == TRANSPORTRECV:' are deleted or commented.
Pushing the green button interrupts the controller and will run the function run_covi(). While running, the LED is turned on.
Pushing the red button interrupts the controller and will stop the function run_covi(). The LED will turn off.
