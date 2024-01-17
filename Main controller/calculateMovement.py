from conn import write_to_serial

XAXISCAM0 = 0                                                               # Index for the measurement value of the X axis on camera 0
YAXISCAM0 = 1                                                               # Index for the measurement value of the Y axis on camera 0
XAXISCAM2 = 2                                                               # Index for the measurement value of the X axis on camera 2
YAXISCAM2 = 3                                                               # Index for the measurement value of the Y axis on camera 2
PIXELSIZE = 9.922                                                           # Size of a single pixel in micrometers
STEPSIZE = .625                                                             # Single step distance in micrometers
MAXSTEPS = 7500                                                             # Maximum steps to set for all directions.

def convert_pixels2steps(data):
    if isinstance(data, float):
        distInUm = PIXELSIZE * data
        stepsToTake = maxsteps_check(distInUm / STEPSIZE)
    else:
        stepsToTake = []
        for i in data:
            distInUm = PIXELSIZE * float(i)
            stepsToTake.append(maxsteps_check(distInUm / STEPSIZE))
    return stepsToTake

def maxsteps_check(steps):
    if steps > MAXSTEPS or steps < -MAXSTEPS:
        steps = 0
    return steps

def move_actuator(data):
    write_to_serial("start")
    YDiff = abs(float(data[YAXISCAM0]) - float(data[YAXISCAM2]))
    stepsToTake = convert_pixels2steps(data)
    if abs(float(data[YAXISCAM0])) > 2.5 or abs(float(data[YAXISCAM2])) > 2.5:
        if YDiff > 4:
            data[YAXISCAM0] = float(data[YAXISCAM0]) * (abs(float(data[YAXISCAM0])) / (abs(float(data[YAXISCAM0])) + abs(float(data[YAXISCAM2]))))
            data[YAXISCAM2] = float(data[YAXISCAM2]) * (abs(float(data[YAXISCAM2])) / (abs(float(data[YAXISCAM0])) + abs(float(data[YAXISCAM2]))))
            stepsToTake = convert_pixels2steps(data)
            stepsToTake[YAXISCAM0] /= 1.92
            stepsToTake[YAXISCAM2] /= 1.92
        write_to_serial(stepsToTake[YAXISCAM0])
        write_to_serial(stepsToTake[YAXISCAM2])
    else:
        write_to_serial(0)
        write_to_serial(0)
        write_to_serial(stepsToTake[XAXISCAM0])
    write_to_serial("end")
