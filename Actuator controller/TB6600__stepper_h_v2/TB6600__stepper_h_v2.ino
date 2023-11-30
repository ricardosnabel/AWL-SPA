#include <AccelStepper.h>

#define errLed        13
#define pulPinX2      10
#define dirPinX2      9
#define enaPinX2      8
#define pulPinX1      7
#define dirPinX1      6
#define enaPinX1      5
#define pulPinY       4
#define dirPinY       3
#define enaPinY       2
#define pixelSize     9.922
#define stepSize      2.5
#define startPosition 0

byte index, status;
int *cam;

AccelStepper stepperX1(1, pulPinX1, dirPinX1);
AccelStepper stepperX2(1, pulPinX2, dirPinX2);
AccelStepper stepperY(1, pulPinY, dirPinY);

void setup() {
  Serial.begin(2000000);
  pinMode(dirPinX1, OUTPUT);
  pinMode(pulPinX1, OUTPUT);
  pinMode(enaPinX1, OUTPUT);
  pinMode(dirPinX2, OUTPUT);
  pinMode(pulPinX2, OUTPUT);
  pinMode(enaPinX2, OUTPUT);
  pinMode(dirPinY, OUTPUT);
  pinMode(pulPinY, OUTPUT);
  pinMode(enaPinY, OUTPUT);

  stepper_innit();

  digitalWrite(enaPinX2, true);
  digitalWrite(enaPinX1, true);
  digitalWrite(enaPinY, true);

  index = 0;
  status = 0;
  cam = 0;
}

void stepper_innit(){
  stepperX1.setMaxSpeed(6400);
  stepperX1.setAcceleration(3200);
  stepperX1.setSpeed(6400);
  stepperX2.setMaxSpeed(6400);
  stepperX2.setAcceleration(3200);
  stepperX2.setSpeed(6400);
  stepperY.setMaxSpeed(6400);
  stepperY.setAcceleration(3200);
  stepperY.setSpeed(6400);
}

void step_direction(int steps, int dirPin){
    if (steps >= 0)
      digitalWrite(dirPin, true);
    else
      digitalWrite(dirPin, false);
}

void PulseSignal(int steps, int enaPin, int dirPin){
  print_serial("Steps: ", steps);
  step_direction(steps, dirPin);
  digitalWrite(enaPin, false);
  if (enaPin == enaPinX1){
    stepperX1.moveTo(steps);
    stepperX1.runToPosition();
    stepperX1.stop();
  } else if (enaPin == enaPinX2){
    stepperX2.moveTo(steps);
    stepperX2.runToPosition();
    stepperX2.stop();
  } else if (enaPin == enaPinY){
    stepperY.moveTo(steps);
    stepperY.runToPosition();
    stepperY.stop();
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
}

void loop() {
  String readSerial;
  int enaPin = 0;
  int dirPin = 0;
  switch (status){
    case 0:
      readSerial = Serial.readString();
      if (readSerial == "start"){
        status = 1;
      }
      break;
    case 1:
      if (Serial.available() > 0){
        readSerial = Serial.readString();
        if (readSerial == "end"){
          index = 0;
          cam = 0;
          status = 0;
        }
        else {
          index++;
          cam[index] = readSerial.toInt();
          status = 2;
        }
      }
      break;
    case 2:
      if (index == 1){
        enaPin = enaPinX1;
        dirPin = dirPinX1;
      }
      else if (index == 2){
        enaPin = enaPinX2;
        dirPin = dirPinX2;
      }
      else if (index == 3){
        enaPin = enaPinY;
        dirPin = dirPinY;
      } else {
        status = 1;
        break;
      }
      print_serial("enaPin: ", enaPin);
      PulseSignal(cam[index], enaPin, dirPin);
      status = 1;
      break;
  }
}
