#include <AccelStepper.h>


#define pulPinX2 10
#define dirPinX2 9
#define enaPinX2 8
#define pulPinX1 7
#define dirPinX1 6
#define enaPinX1 5
#define pulPinY 4
#define dirPinY 3
#define enaPinY 2
#define errLed 13

#define startPosition 0

int stepsToTakeX = -1;
int startUp, startTime, endTime, waitTime;
bool dirMotor, dirMotorY, conEnable, onOff;

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
  dirMotor = true;
  dirMotorY = true;
  conEnable = true;
  digitalWrite(enaPinX2, true);
  digitalWrite(enaPinX1, true);
  digitalWrite(enaPinY, true);
  onOff = true;

  stepper_innit(stepperX1);
  stepper_innit(stepperX2);
  stepper_innit(stepperY);
}

void stepper_innit(AccelStepper stepper){
  stepper.setMaxSpeed(6400);
  stepper.setAcceleration(6400);
  stepper.setSpeed(3200);
}

void PulseSignal(int steps, AccelStepper stepper){
  delay(1000);
  startTime = millis();
  stepper.moveTo(steps);
  stepper.runToPosition();
  endTime = millis();
  delay(1000);
  stepper.stop();
}

void loop() {
  if (Serial.available() > 0){
    int incomingData = Serial.readString().toInt();
    if (incomingData > 0){
      dirMotor = true;
    } else {
      dirMotor = false;
    }
    stepsToTakeX = incomingData;
    Serial.println(incomingData);
  } if ((millis() - waitTime) > 5000){
    digitalWrite(enaPinX2, true);
  }
  if (onOff && stepsToTakeX >= 0){
    digitalWrite(enaPinX2, false);
    PulseSignal(stepsToTakeX, stepperX2);
    stepsToTakeX = -1;
    Serial.println(endTime - startTime);
    waitTime = millis();
  }
}
