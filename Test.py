import math
import time

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
OMRONCONTROLLER = ['10.5.5.100', 9876]
EXTERNCONTROLLER = ['127.0.0.1', 0]
runApp = False
countSteps = [0, 0, 0] # [Y1, Y2, X]
test_data = ['OK\r', ['-240.5077', '356.2894', '160.6148', '169.1143\r']]
'''
def convert_um2steps(data):
    if isinstance(data, float):
        stepsToTake = (data / STEPSIZE) #- -64941.17647058824
    else:
        stepsToTake = []
        for i in data:
            stepsToTake.append((i / STEPSIZE)) #- -64941.17647058824)
    return stepsToTake

def convert_pixels2um(data):
    if isinstance(data, float):
        distInUm = PIXELSIZE * data
    else:
        distInUm = []
        for i in data:
            distInUm.append(PIXELSIZE * float(i))
    print("DistInUm: ", distInUm)
    return distInUm

def maxsteps_check(steps):
    if steps > MAXSTEPS:
        steps = MAXSTEPS
    elif steps < -MAXSTEPS:
        steps = -MAXSTEPS
    return steps

def temp_name(data):
    xPos0 = float(data[XAXISCAM0])
    xPos2 = float(data[XAXISCAM2])
    if xPos0 > xPos2:
        pointDiff = xPos0 / xPos2
    elif xPos2 > xPos0:
        pointDiff = xPos2 / xPos0
    return pointDiff


def rotate(data):
    xPos0 = float(data[XAXISCAM0])
    xPos2 = float(data[XAXISCAM2])
    epsilon = abs(convert_pixels2um(xPos0) - convert_pixels2um(xPos2))
    n = ((4 / (XMOTORDISTANCE * XMOTORDISTANCE)) * ((DISTANCEX * DISTANCEX) + (DISTANCEY * DISTANCEY)))
    m = ((2*epsilon) / XMOTORDISTANCE) * DISTANCEY
    p = ((epsilon * epsilon) / 4) - (DISTANCEX * DISTANCEX)
    sqrtcalc = math.sqrt((m*m) - (4 * n * p))
    d = ((-m - sqrtcalc) / (2 * n)) - DZEROVALUE
    stepsToTake = convert_um2steps(d)
    if xPos0 > xPos2:
        stepsToTake = [stepsToTake, stepsToTake * (xPos0 / xPos2)]
    elif xPos2 > xPos0:
        stepsToTake = [stepsToTake * (xPos2 / xPos0), stepsToTake]
    print("Epsilon: ", epsilon)
    print("N: ", n)
    print("M: ", m)
    print("P: ", p)
    print("Sqrtcalc: ", sqrtcalc)
    print("d: ", d)
    print("Steps: ", stepsToTake)
    print()
    return stepsToTake

def move_actuator(data):
    print("Data: ", data)

    diff = abs(abs(float(data[YAXISCAM0])) - abs(float((data[YAXISCAM2]))))
    relPos0 = (float(data[YAXISCAM0]) / (abs(float(data[YAXISCAM0])) + abs(float(data[YAXISCAM2])))) * diff
    relPos2 = (float(data[YAXISCAM2]) / (abs(float(data[YAXISCAM0])) + abs(float(data[YAXISCAM2])))) * diff

    print("Diff: ", diff)
    print("Relpos0: ", relPos0)
    print("Relpos2: ", relPos2)
    print("YAxisCam0: ", data[YAXISCAM0])
    print("YAxisCam2: ", data[YAXISCAM2])

    data[YAXISCAM2] = float(data[YAXISCAM2]) - relPos2
    data[YAXISCAM0] = float(data[YAXISCAM0]) - relPos0

    print("YAxisCam0: ", data[YAXISCAM0])
    print("YAxisCam2: ", data[YAXISCAM2])

    stepsToTake = convert_um2steps(convert_pixels2um(data))

    print("StepsYAxisCam0: ", stepsToTake[YAXISCAM0] / 2)
    print("StepsYAxisCam2: ", stepsToTake[YAXISCAM2] / 2)
    print()

# current calculations on the rotations.
def rotate(data):
    epsilon = abs(convert_pixels2um(float(data[XAXISCAM0])) - convert_pixels2um(float(data[XAXISCAM2])))
    n = ((4 / (XMOTORDISTANCE * XMOTORDISTANCE)) * ((DISTANCEX * DISTANCEX) + (DISTANCEY * DISTANCEY)))
    m = (((DISTANCEY*2) * epsilon) / XMOTORDISTANCE)
    p = ((epsilon * epsilon) / 4) - (DISTANCEX * DISTANCEX)
    sqrtcalc = (m*m) - (4 * n * p)
    calc = (m - math.sqrt(abs(sqrtcalc))) / (2 * n)
    stepsToTake = convert_um2steps(calc)
    if sqrtcalc < 0:
        stepsToTake = -stepsToTake
    print("Epsilon: ", epsilon)
    print("N: ", n)
    print("M: ", m)
    print("P: ", p)
    print("Calc: ", calc)
    print("Steps: ", stepsToTake)
    return stepsToTake

if __name__ == '__main__':
    # originele dataset = ['-265.8202', '478.1003', '149.0438', '-339.4766']

    data = ['-24.5077', '356.2894', '16.6148', '169.1143\r']
    print("Test 1: ")
    move_actuator(data)
    
    data = ['-24.5077', '-16.1143', '16.6148', '-356.2894\r']
    print("Test 2: ")
    move_actuator(data)'''

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
            data[YAXISCAM0] = float(data[YAXISCAM0]) * (abs(float(data[YAXISCAM0])) / (abs(float(data[YAXISCAM0])) + abs(float(data[YAXISCAM2]))))
            data[YAXISCAM2] = float(data[YAXISCAM2]) * (abs(float(data[YAXISCAM2])) / (abs(float(data[YAXISCAM0])) + abs(float(data[YAXISCAM2]))))
            stepsToTake = convert_pixels2steps(data)
            #stepsToTake[YAXISCAM0] /= 2
            #stepsToTake[YAXISCAM2] /= 2
        write = handle_countSteps([stepsToTake[YAXISCAM0], stepsToTake[YAXISCAM2], 0], False, False)
        test_data[MEASUREDDATA][YAXISCAM0] *= 0.8
        test_data[MEASUREDDATA][YAXISCAM2] *= 0.8
        print(write)
    else:
        print("x movement")
        stepsToTake = convert_pixels2steps(data)
        write = handle_countSteps([0, 0, stepsToTake[XAXISCAM0]], False, False)
        test_data[MEASUREDDATA][XAXISCAM0] *= 0.8
        test_data[MEASUREDDATA][XAXISCAM2] *= 0.8
        print(write)

def to_neutral(steps):
    for i in range(len(steps)):
        if steps[i] >= 0:
            steps[i] = -steps[i]
        else:
            steps[i] = abs(steps[i])
    print("Steps to neutral: ", steps)
    return steps

def handle_countSteps(steps, clear, getcount):
    global countSteps
    if clear:
        countSteps = [0, 0, 0]
        print("Clear countSteps: ", countSteps)
        return 0
    if getcount:
        print("Current countSteps: ", countSteps)
        return countSteps
    else:
        for i in range(len(steps)):
            if abs(countSteps[i] + steps[i]) >= MAXSTEPS:
                steps[i] = 0
            else:
                countSteps[i] += steps[i]
        print("Max step check: ", steps)
        print("Countstep check: ", countSteps)
        return steps

def handle_test():
    check_pos = 0
    for i in range(len(test_data[MEASUREDDATA])):
        test_data[MEASUREDDATA][i] = float(test_data[MEASUREDDATA][i])
        if test_data[MEASUREDDATA][i] < 5.0:
            check_pos += 1
            print(check_pos)
    if check_pos >= 4:
        print(test_data)
        test_data[MEASUREDDATA] = ['READY\r']

def handle_data(status):
    while True:
        match status:
            case 'waiting for plate':
                handle_countSteps(0, True, False)
                print()
                time.sleep(2)
                status = 'plate arrived'
            case 'plate arrived':
                status = 'unaligned'
            case 'unaligned':
                    handle_test()
                    time.sleep(.5)
                    data = test_data
                    print(data)
                    if data[MEASUREDDATA][0] == 'READY\r':
                        status = 'aligned'
                    else:
                        move_actuator(data[MEASUREDDATA])
                        print()
            case 'aligned':
                time.sleep(2)
                status = 'wait for external module'
            case 'wait for external module':
                time.sleep(2)
                status = 'return to neutral'
            case 'return to neutral':
                to_neutral(handle_countSteps(0, False, True))
                print()
                status = 'waiting for plate'

if __name__ == '__main__':
    status = 'waiting for plate'
    handle_data(status)

