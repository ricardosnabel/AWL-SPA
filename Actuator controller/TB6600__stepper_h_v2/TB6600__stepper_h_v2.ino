#include <AccelStepper.h>


#define pulPinX 7
#define dirPinX 6
#define enaPinX 5
#define pulPinY 4
#define dirPinY 3
#define enaPinY 2
#define errLed 13

#define startPosition 0

int stepsToTakeX = -1;
int startUp, startTime, endTime, waitTime;
bool dirMotor, dirMotorY, conEnable, onOff;

AccelStepper stepperX(1, pulPinX, dirPinX);
AccelStepper stepperY(1, pulPinY, dirPinY);

void setup() {
  Serial.begin(2000000);
  pinMode(dirPinX, OUTPUT);
  pinMode(pulPinX, OUTPUT);
  pinMode(enaPinX, OUTPUT);
  pinMode(dirPinY, OUTPUT);
  pinMode(pulPinY, OUTPUT);
  pinMode(enaPinY, OUTPUT);
  dirMotor = true;
  dirMotorY = true;
  conEnable = true;
  digitalWrite(enaPinX, true);
  digitalWrite(enaPinY, true);
  onOff = true;

  stepperX.setMaxSpeed(6400);
  stepperX.setAcceleration(6400);
  stepperX.setSpeed(3200);
}

void PulseSignal(int steps){
  delay(1000);
  startTime = millis();
  stepperX.moveTo(steps);
  stepperX.runToPosition();
  endTime = millis();
  delay(1000);
  stepperX.stop();
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
    digitalWrite(enaPinX, true);
  }
  if (onOff && stepsToTakeX >= 0){
    digitalWrite(enaPinX, false);
    PulseSignal(stepsToTakeX);
    stepsToTakeX = -1;
    Serial.println(endTime - startTime);
    waitTime = millis();
  }
}
