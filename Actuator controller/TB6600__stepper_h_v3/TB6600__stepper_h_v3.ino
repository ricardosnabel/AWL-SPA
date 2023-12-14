#include <AccelStepper.h>
#include <Arduino_FreeRTOS.h>
#include <queue.h>

#define errLed        13
#define pulPinY2      10
#define dirPinY2      9
#define enaPinY2      8
#define pulPinY1      7
#define dirPinY1      6
#define enaPinY1      5
#define pulPinX       4
#define dirPinX       3
#define enaPinX       2
#define pixelSize     9.922
#define stepSize      2.5
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
  if (enaPin == enaPinY1){
    stepperX1.moveTo(steps);
    stepperX1.runToPosition();
    stepperX1.stop();
  } else if (enaPin == enaPinY2){
    stepperX2.moveTo(steps);
    stepperX2.runToPosition();
    stepperX2.stop();
  } else if (enaPin == enaPinX){
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
        enaPin = enaPinY1;
        dirPin = dirPinY1;
      }
      else if (index == 2){
        enaPin = enaPinY2;
        dirPin = dirPinY2;
      }
      else if (index == 3){
        enaPin = enaPinX;
        dirPin = dirPinX;
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
