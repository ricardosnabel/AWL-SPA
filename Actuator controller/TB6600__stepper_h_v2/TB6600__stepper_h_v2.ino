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
  digitalWrite(enaPinY1, true);
  digitalWrite(enaPinY2, true);
  digitalWrite(enaPinX, true);
}

void stepper_innit(){
  stepperY1.setMaxSpeed(3200);
  stepperY1.setAcceleration(400);
  stepperY1.setSpeed(3200);
  stepperY2.setMaxSpeed(3200);
  stepperY2.setAcceleration(400);
  stepperY2.setSpeed(3200);
  stepperX.setMaxSpeed(3200);
  stepperX.setAcceleration(400);
  stepperX.setSpeed(3200);
}

void loop() {
  float readMotorY1 = 0.0;
  float readMotorY2 = 0.0;
  float readMotorX = 0.0;
  uint8_t enaPin = 0;
  uint8_t dirPin = 0;

  if (Serial.available() > 0){
    readMotorY1 = Serial.readStringUntil(';').toFloat();
    readMotorY2 = Serial.readStringUntil(';').toFloat();
    readMotorX  = Serial.readStringUntil(';').toFloat();

    Serial.println(readMotorY1);
    Serial.println(readMotorY2);
    Serial.println(readMotorX);

    stepperY1.moveTo(readMotorY1);
    stepperY2.moveTo(readMotorY2);
    stepperX.moveTo(readMotorX);



    while((abs(stepperY1.distanceToGo()) != 0) || (abs(stepperY2.distanceToGo()) != 0) || (abs(stepperX.distanceToGo()) != 0)){
      digitalWrite(enaPinY1, false);
      digitalWrite(enaPinY2, false);
      digitalWrite(enaPinX, false);

      stepperY1.run();
      stepperY2.run();
      stepperX.run();

      digitalWrite(enaPinY1, true);
      digitalWrite(enaPinY2, true);
      digitalWrite(enaPinX, true);
      Serial.println(stepperY1.distanceToGo());
      Serial.println(stepperY2.distanceToGo());
      Serial.println(stepperX.distanceToGo());
    }

    if ((abs(stepperY1.distanceToGo()) == 0) && (abs(stepperY2.distanceToGo()) == 0) && (abs(stepperX.distanceToGo()) == 0)){
      Serial.println("end");
    }

  }
}
