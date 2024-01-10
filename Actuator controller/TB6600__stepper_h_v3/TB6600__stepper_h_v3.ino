#include <AccelStepper.h>

#define pulPinY2      10
#define dirPinY2      9
#define enaPinY2      8
#define pulPinY1      7
#define dirPinY1      6
#define enaPinY1      5
#define pulPinX       4
#define dirPinX       3
#define enaPinX       2
#define startPosition 0

byte index, status;
int *cam;

AccelStepper stepperX1(1, pulPinY1, dirPinY1);
AccelStepper stepperX2(1, pulPinY2, dirPinY2);
AccelStepper stepperY(1, pulPinX, dirPinX);

void setup() {
  Serial.begin(2000000);
  pinMode(dirPinY1, OUTPUT);
  pinMode(pulPinY1, OUTPUT);
  pinMode(enaPinY1, OUTPUT);
  pinMode(dirPinY2, OUTPUT);
  pinMode(pulPinY2, OUTPUT);
  pinMode(enaPinY2, OUTPUT);
  pinMode(dirPinX, OUTPUT);
  pinMode(pulPinX, OUTPUT);
  pinMode(enaPinX, OUTPUT);

  stepper_innit();

  digitalWrite(enaPinY2, true);
  digitalWrite(enaPinY1, true);
  digitalWrite(enaPinX, true);

  index = 0;
  status = 0;
  cam = 0;
}

void stepper_innit(){
  stepperX1.setMaxSpeed(1600);
  stepperX1.setAcceleration(200);
  stepperX1.setSpeed(1600);
  stepperX2.setMaxSpeed(1600);
  stepperX2.setAcceleration(200);
  stepperX2.setSpeed(1600);
  stepperY.setMaxSpeed(1600);
  stepperY.setAcceleration(200);
  stepperY.setSpeed(1600);
  stepperX1.setMaxSpeed(3200);
  stepperX1.setAcceleration(400);
  stepperX1.setSpeed(3200);
  stepperX2.setMaxSpeed(3200);
  stepperX2.setAcceleration(400);
  stepperX2.setSpeed(3200);
  stepperY.setMaxSpeed(3200);
  stepperY.setAcceleration(400);
  stepperY.setSpeed(3200);
}

void step_direction(int steps, int dirPin){
    if (steps > 0)
      digitalWrite(dirPin, true);
    else
      digitalWrite(dirPin, false);
}

void PulseSignal(int steps, int enaPin, int dirPin){
  print_serial("Steps: ", steps);
  step_direction(steps, dirPin);
  digitalWrite(enaPin, false);
  if (enaPin == enaPinY1){
    stepperX1.moveTo(steps);
    stepperX1.runToPosition();
    stepperX1.stop();
    stepperX1.setCurrentPosition(0);
  } else if (enaPin == enaPinY2){
    stepperX2.moveTo(steps);
    stepperX2.runToPosition();
    stepperX2.stop();
    stepperX2.setCurrentPosition(0);
  } else if (enaPin == enaPinX){
    stepperY.moveTo(steps);
    stepperY.runToPosition();
    stepperY.stop();
    stepperY.setCurrentPosition(0);
  }
  digitalWrite(enaPin, true);
}

void print_serial(int data){
  Serial.println(data);
}

void print_serial(String data){
  Serial.println(data);
}

void print_serial(String txtData, int numData){
  Serial.print(txtData);
  Serial.println(numData);

