#include <AccelStepper.h>
#include <Arduino_FreeRTOS.h>
#include <queue.h>
#include <semphr.h>

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
#define NO_OF_ITEMS   6
#define Y1            1
#define Y2            2
#define X             3

// Function declerations
void motor_innit();
void stepper_innit();
void vTaskReadSerial(void *pvParameters);
void vTaskWriteSerial(void *pvParameters);
void vTaskSignalMotor(void *pvParameters);
void vTaskCalibrate(void *pvParameters);
void step_direction(int steps, int dirPin);

typedef struct{
  uint8_t motor;
  uint16_t steps;
} queue_data;

// FreeRTOS Handles
QueueHandle_t xQueueSteps;
SemaphoreHandle_t xSemSerial;
SemaphoreHandle_t xSemSetDone;

// Global variables
bool done;
AccelStepper stepperY1(1, pulPinY1, dirPinY1);
AccelStepper stepperY2(1, pulPinY2, dirPinY2);
AccelStepper stepperX(1, pulPinX, dirPinX);

/* 
*  To do:
*  Calibreren
*/

void setup() {
  Serial.setTimeout(2);
  Serial.begin(115200);
  xTaskCreate(vTaskReadSerial, "Read Serial", 100, NULL, tskIDLE_PRIORITY, NULL);
  xTaskCreate(vTaskWriteSerial, "Write Serial", 100, NULL, tskIDLE_PRIORITY, NULL);
  xTaskCreate(vTaskSignalMotor, "Signal motor", 100, NULL, tskIDLE_PRIORITY, NULL);
  xTaskCreate(vTaskCalibrate, "Calibrate system", 100, NULL, tskIDLE_PRIORITY, NULL);

  xQueueSteps = xQueueCreate(NO_OF_ITEMS, sizeof(queue_data));
  xSemSerial = xSemaphoreCreateBinary();
  xSemSetDone = xSemaphoreCreateBinary();

  stepper_innit();
  motor_innit();
}

void motor_innit(){
  pinMode(dirPinY1, OUTPUT);
  pinMode(pulPinY1, OUTPUT);
  pinMode(enaPinY1, OUTPUT);
  pinMode(dirPinY2, OUTPUT);
  pinMode(pulPinY2, OUTPUT);
  pinMode(enaPinY2, OUTPUT);
  pinMode(dirPinX, OUTPUT);
  pinMode(pulPinX, OUTPUT);
  pinMode(enaPinX, OUTPUT);


  digitalWrite(enaPinY2, true);
  digitalWrite(enaPinY1, true);
  digitalWrite(enaPinX, true);
}

void stepper_innit(){
  stepperY1.setMaxSpeed(6400);
  stepperY1.setAcceleration(3200);
  stepperY1.setSpeed(6400);
  stepperY2.setMaxSpeed(6400);
  stepperY2.setAcceleration(3200);
  stepperY2.setSpeed(6400);
  stepperX.setMaxSpeed(6400);
  stepperX.setAcceleration(3200);
  stepperX.setSpeed(6400);
}

void vTaskReadSerial(void *pvParameters){
  queue_data received_data;
  for(;;){
    if (Serial.available()){
      xSemaphoreTake(xSemSerial, portMAX_DELAY);
      uint8_t readMotor = Serial.readStringUntil(';').toInt();
      uint16_t readSteps = Serial.readStringUntil('\r').toInt();
      xSemaphoreGive(xSemSerial);
      if (readMotor && readSteps){
        received_data.motor = readMotor;
        received_data.steps = readSteps;
        xQueueSendToBack(xQueueSteps, &received_data, portMAX_DELAY);
      }
    }
  }
}

void vTaskWriteSerial(void *pvParameters){
  for(;;){
    if (done){
      xSemaphoreTake(xSemSerial, portMAX_DELAY);
      Serial.print("Done");
      xSemaphoreGive(xSemSerial);
      xSemaphoreTake(xSemSetDone, portMAX_DELAY);
      done = false;
      xSemaphoreGive(xSemSetDone);
    }
  }
}

void vTaskSignalMotor(void *pvParameters){
  queue_data read_queue;
  for(;;){
    while (xQueueReceive(xQueueSteps, &read_queue, portMAX_DELAY)){
      if (read_queue.motor == Y1){
        step_direction(read_queue.steps, dirPinY1);
        digitalWrite(enaPinY1, false);
        stepperY1.moveTo(read_queue.steps);
        stepperY1.runToPosition();
        stepperY1.stop();
        stepperY1.setCurrentPosition(0);
        digitalWrite(enaPinY1, true);
      } if (read_queue.motor == Y2){
        step_direction(read_queue.steps, dirPinY2);
        digitalWrite(enaPinY2, false);
        stepperY2.moveTo(read_queue.steps);
        stepperY2.runToPosition();
        stepperY2.stop();
        stepperY2.setCurrentPosition(0);
        digitalWrite(enaPinY2, true);
      } if (read_queue.motor == X){
        step_direction(read_queue.steps, dirPinX);
        digitalWrite(enaPinX, false);
        stepperX.moveTo(read_queue.steps);
        stepperX.runToPosition();
        stepperX.stop();
        stepperX.setCurrentPosition(0);
        digitalWrite(enaPinX, true);
      }
    }
    xSemaphoreTake(xSemSetDone, portMAX_DELAY);
    done = true;
    xSemaphoreGive(xSemSetDone);
  }
}

void vTaskCalibrate(void *pvParameters){

}

void step_direction(int steps, int dirPin){
    if (steps >= 0)
      digitalWrite(dirPin, true);
    else
      digitalWrite(dirPin, false);
}

void loop(){

}
