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
DISTANCES = [85250, 70000, 177250]
MATRIX = [[1, -0.39492242595204513398, 0.39492242595204513398], [0, 1, 0], [0, 0.0000056417489421720733427, -0.0000056417489421720733427]]
DISTANCEX = 262500 / 2
DISTANCEY = 140000 / 2
XMOTORDISTANCE = 92000 # distance between two translation points
DZEROVALUE = -40588.23529411765
OMRONCONTROLLER = ['10.5.5.100', 9876]
EXTERNCONTROLLER = ['127.0.0.1', 0]
runApp = False
countSteps = [0, 0, 0] # [Y1, Y2, X]
test_data1 = ['OK\r', ['-150.8992', '232.9294', '140.4246', '-296.4908\r']]
test_data2 = ['OK\r', ['-240.5077', '-356.2894', '-160.6148', '-169.1143\r']]
test_data3 = ['OK\r', ['240.5077', '356.2894', '160.6148', '169.1143\r']]
test_data4 = ['OK\r', ['240.5077', '-356.2894', '160.6148', '-169.1143\r']]
test_data_arr = [test_data1, test_data2, test_data3, test_data4]

def convert_pixels2um(data):
    if isinstance(data, float):
        distInUm = PIXELSIZE * data
    else:
        distInUm = []
        for i in data:
            distInUm.append(PIXELSIZE * float(i))
    return distInUm

def convert_um2steps(data):
    if isinstance(data, float):
        stepsToTake = data / STEPSIZE
    else:
        stepsToTake = []
        for i in data:
            stepsToTake.append(i / STEPSIZE)
    return stepsToTake

def maxsteps_check(steps):
    if steps > MAXSTEPS:
        steps = MAXSTEPS
    elif steps < -MAXSTEPS:
        steps = -MAXSTEPS
    return steps

def rotate(data):
    xPos0 = float(data[XAXISCAM0])
    xPos2 = float(data[XAXISCAM2])
    epsilon = abs((convert_pixels2um(xPos0) + DISTANCEX) - (convert_pixels2um(xPos2) - DISTANCEX))
    n = ((4 / (XMOTORDISTANCE * XMOTORDISTANCE)) * ((DISTANCEX * DISTANCEX) + (DISTANCEY * DISTANCEY)))
    m = ((2*epsilon) / XMOTORDISTANCE) * DISTANCEY
    p = ((epsilon * epsilon) / 4) - (DISTANCEX * DISTANCEX)
    sqrtcalc = math.sqrt((m*m) - (4 * n * p))
    d = ((-m + sqrtcalc) / (2 * n))
    stepsToTake = abs(convert_um2steps(d))
    if abs(xPos0) > abs(xPos2):
        #stepsToTake = [stepsToTake, stepsToTake * (abs(xPos0) / abs(xPos2))]
        posDif = abs(xPos0) / abs(xPos2)
    elif abs(xPos2) > abs(xPos0):
        #stepsToTake = [stepsToTake * (abs(xPos2) / abs(xPos0)), stepsToTake]
        posDif = abs(xPos2) / abs(xPos0)
    print("Epsilon: ", epsilon)
    print("N: ", n)
    print("M: ", m)
    print("P: ", p)
    print("Sqrtcalc: ", sqrtcalc)
    print("d: ", d)
    print("Steps: ", stepsToTake)
    print()
    print(stepsToTake + (stepsToTake * posDif))

def movement(data):
    datainUm = convert_pixels2um(data)
    print(datainUm)
    delta = [((datainUm[XAXISCAM2]) * MATRIX[0][0]) + ((datainUm[YAXISCAM2]) * MATRIX[0][1]) + (datainUm[YAXISCAM0] * MATRIX[0][2]), # X
             ((datainUm[XAXISCAM2]) * MATRIX[1][0]) + ((datainUm[YAXISCAM2]) * MATRIX[1][1]) + (datainUm[YAXISCAM0] * MATRIX[1][2]), # Y1
             ((datainUm[XAXISCAM2]) * MATRIX[2][0]) + ((datainUm[YAXISCAM2]) * MATRIX[2][1]) + (datainUm[YAXISCAM0] * MATRIX[2][2])] # Delta
    print("Delta: ", delta)
    print()
    print(delta[2] * (DISTANCES[2] - DISTANCES[0]))
    print(DISTANCES[2] - DISTANCES[0])
    delta[2] = delta[1] + (abs(delta[2]) * (DISTANCES[2] - DISTANCES[0]))
    print("Delta2: ", delta)
    print()
    stepsToTake = convert_um2steps(delta)
    print([stepsToTake[2], stepsToTake[1], stepsToTake[0]])

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

'''def handle_test():
    check_pos = 0
    for i in range(len(test_data[MEASUREDDATA])):
        test_data[MEASUREDDATA][i] = float(test_data[MEASUREDDATA][i])
        if test_data[MEASUREDDATA][i] < 5.0:
            check_pos += 1
            print(check_pos)
        #test_data[MEASUREDDATA][i] *= 0.7
    if check_pos >= 4:
        print(test_data)
        test_data[MEASUREDDATA] = ['READY\r']'''

def handle_data(status):
    i = 0
    while i < 4:
        match status:
            case 'waiting for plate':
                handle_countSteps(0, True, False)
                print()
                time.sleep(2)
                status = 'plate arrived'
            case 'plate arrived':
                status = 'unaligned'
            case 'unaligned':
                    #handle_test()
                    time.sleep(1)
                    test_data = test_data_arr[i]
                    data = test_data
                    print(data)
                    if data[MEASUREDDATA][0] == 'READY\r':
                        status = 'aligned'
                    else:
                        movement(data[MEASUREDDATA])
                        print()
                        rotate(data[MEASUREDDATA])
                        print()
                        i+=1
                        
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

