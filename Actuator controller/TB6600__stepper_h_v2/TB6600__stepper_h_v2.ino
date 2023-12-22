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

AccelStepper stepperY1(1, pulPinY1, dirPinY1);
AccelStepper stepperY2(1, pulPinY2, dirPinY2);
AccelStepper stepperX(1, pulPinX, dirPinX);

void setup() {
  Serial.setTimeout(2);
  Serial.begin(115200);
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
}

void stepper_innit(){
  stepperY1.setMaxSpeed(3200);
  stepperY1.setAcceleration(400);
  stepperY1.setSpeed(3200);
  stepperY1.setEnablePin(enaPinY1);
  stepperY2.setMaxSpeed(3200);
  stepperY2.setAcceleration(400);
  stepperY2.setSpeed(3200);
  stepperY2.setEnablePin(enaPinY2);
  stepperX.setMaxSpeed(3200);
  stepperX.setAcceleration(400);
  stepperX.setSpeed(3200);
  stepperX.setEnablePin(enaPinX);
}

void loop() {
  uint8_t readMotorY1;
  uint8_t readMotorY2;
  uint8_t readMotorX;
  uint16_t readSteps;
  uint8_t enaPin = 0;
  uint8_t dirPin = 0;

  if (Serial.available() > 0){
    readMotorY1 = Serial.readStringUntil(';').toInt();
    readMotorY2 = Serial.readStringUntil(';').toInt();
    readMotorX  = Serial.readStringUntil(';').toInt();

    stepperY1.moveTo(readMotorY1);
    stepperY2.moveTo(readMotorY2);
    stepperX.moveTo(readMotorX);

    while((abs(stepperY1.distanceToGo()) != 0) || (abs(stepperY2.distanceToGo()) != 0) || (abs(stepperX.distanceToGo()) != 0)){
      stepperY1.run();
      stepperY2.run();
      stepperX.run();
    }

    if ((abs(stepperY1.distanceToGo()) == 0) && (abs(stepperY2.distanceToGo()) == 0) && (abs(stepperX.distanceToGo()) == 0)){
      Serial.println("end");
    }

  }
}
