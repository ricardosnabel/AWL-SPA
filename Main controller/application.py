from conn import measure, aligned, omron_recv, transport_recv, screenprint_recv
from calculateMovement import move_actuator
from gpio import get_runApp, set_runApp

MEASUREDDATA = 2                                                            # Index for the measurement data received from the Omron controller
TRANSPORTRECV = 'OK\r'                                                      # Message to receive to run the controller

def run_covi(status):
    while True:
        while get_runApp():
            match status:
                case 'waiting for plate':
                    #transportdata = transport_recv()
                    #if transportdata[0] == TRANSPORTRECV:
                    status = 'unaligned'
                case 'unaligned':
                    measure()
                    data = omron_recv()
                    print(data)
                    if data[MEASUREDDATA][0] != 'ERR\r':
                        status = 'aligning'
                case 'aligning':
                    if data[MEASUREDDATA][0] == 'OK':
                        set_runApp(False)
                        status = 'unaligned'
                    else:
                        move_actuator(data[MEASUREDDATA])
                        state = 'plate arrived'
                case 'aligned':
                    #aligned()
                    status = 'wait for screen print'
                case 'wait for screen print':
                    #if screenprint_recv() == 'OK\r':
                    status = 'return to neutral'
                case 'return to neutral':
                    # insert code to return the actuators to their neutral position
                    status = 'waiting for plate'
