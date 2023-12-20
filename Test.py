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
    print("StepsToTake: ", stepsToTake)
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

def rotate(data):
    epsilon = abs(convert_pixels2um(float(data[XAXISCAM0]))) - abs(convert_pixels2um(float(data[XAXISCAM2])))
    n = ((4 / (XMOTORDISTANCE * XMOTORDISTANCE)) * ((DISTANCEX * DISTANCEX) + (DISTANCEY * DISTANCEY)))
    m = ((2*epsilon) / XMOTORDISTANCE) * DISTANCEY
    p = ((epsilon * epsilon) / 4) - (DISTANCEX * DISTANCEX)
    sqrtcalc = math.sqrt((m*m) - (4 * n * p))
    d = (-m - sqrtcalc) / (2 * n)
    stepsToTake = convert_um2steps(d)
    print("Epsilon: ", epsilon)
    print("N: ", n)
    print("M: ", m)
    print("P: ", p)
    print("Sqrtcalc: ", sqrtcalc)
    print("d: ", d)
    print()
    return stepsToTake

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

    data = ['-265.8202', '478.1003', '149.0438', '-339.4766']
    print("Test 1: ")
    rotate(data)

    data = ['0', '478.1003', '0', '339.4766']
    print("Test 2: ")
    rotate(data)
    
    data = ['26.8202', '478.1003', '-149.0438', '339.4766']
    print("Test 3: ")
    rotate(data)

    data = ['0', '478.1003', '0', '339.4766']
    print("Test 4: ")
    rotate(data)
    data = ['26.8202', '478.1003', '-149.0438', '339.4766']
    print("Test 1: ")
    rotate(data)

    data = ['0', '478.1003', '0', '339.4766']
    print("Test 2: ")
    rotate(data)