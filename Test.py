import math

MEASUREDDATA = 1
XAXISCAM0 = 0
YAXISCAM0 = 1
XAXISCAM2 = 2
YAXISCAM2 = 3
MEASURE = 'M'
LAYOUT = 'DLN 0 1'
DISTANCEX = 262500 / 2
DISTANCEY = 140000 / 2
XMOTORDISTANCE = 92000 # distance between two translation points
DZEROVALUE = -40588.23529411765
PIXELSIZE = 9.922
STEPSIZE = .625
MAXSTEPS = 7500 # test maximum

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
'''def rotate(data):
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
    return stepsToTake'''

if __name__ == '__main__':
    # originele dataset = ['-265.8202', '478.1003', '149.0438', '-339.4766']

    data = ['-24.5077', '356.2894', '16.6148', '169.1143\r']
    print("Test 1: ")
    move_actuator(data)
    
    data = ['-24.5077', '-16.1143', '16.6148', '-356.2894\r']
    print("Test 2: ")
    move_actuator(data)
