#include <AccelStepper.h>
#include <MultiStepper.h>

#define pulPinY2      10
#define dirPinY2      9
#define enaPinY2      8
#define pulPinY1      7
#define dirPinY1      6
#define enaPinY1      5
#define pulPinX       4
#define dirPinX       3
#define enaPinX       2
#define Y1            0
#define Y2            1
#define X             2

AccelStepper stepperY1(1, pulPinY1, dirPinY1);
AccelStepper stepperY2(1, pulPinY2, dirPinY2);
AccelStepper stepperX(1, pulPinX, dirPinX);

//MultiStepper steppers;

void setup() {
  Serial.setTimeout(2);
  Serial.begin(9600);
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
  stepperX.setMaxSpeed(3200);
  stepperX.setAcceleration(400);
  stepperX.setSpeed(3200);
  stepperY2.setMaxSpeed(3200);
  stepperY2.setAcceleration(400);
  stepperY2.setSpeed(3200);
  stepperY1.setMaxSpeed(3200);
  stepperY1.setAcceleration(400);
  stepperY1.setSpeed(3200);

  //steppers.addStepper(stepperY1);
  //steppers.addStepper(stepperY2);
  //steppers.addStepper(stepperX);
}

long step_direction(long steps, uint8_t dirPin){
  if (steps < 0)
    digitalWrite(dirPin, true);
  else
    digitalWrite(dirPin, false);
  return abs(steps);
}

void loop() {
  long positions[3];

  if (Serial.available() >= 0){
    positions[Y1] = Serial.readStringUntil(';').toInt();
    positions[Y2] = Serial.readStringUntil(';').toInt();
    positions[X]  = Serial.readStringUntil(';').toInt();

    //step_direction(positions[Y1], dirPinY1);
    //step_direction(positions[Y2], dirPinY2);
    //step_direction(positions[X], dirPinX);

    //steppers.moveTo(positions);
    stepperY1.moveTo(positions[Y1]);
    stepperY2.moveTo(positions[Y2]);
    stepperX.moveTo(positions[X]);


    digitalWrite(enaPinY1, false);
    digitalWrite(enaPinY2, false);
    digitalWrite(enaPinX, false);
    delay(2000);

    //steppers.runSpeedToPosition();
    stepperY1.runToPosition();

    delay(2000);
    
    stepperY2.runToPosition();

    delay(2000);
    
    stepperX.runToPosition();

    delay(2000);


    digitalWrite(enaPinY1, true);
    digitalWrite(enaPinY2, true);
    digitalWrite(enaPinX, true);

    Serial.println("end");
  }
}
