#include <Servo.h>

// Servos
Servo baseServo;     // pin 3
Servo servoA1;       // pin 4
Servo servoA2;       // pin 5
Servo servoB;        // pin 6
Servo wristA;        // pin 9
Servo wristB;        // pin 10
Servo gripper;       // pin 11

int currentAngle = 90;

void attachAll() {
  baseServo.attach(3);
  servoA1.attach(4);
  servoA2.attach(5);
  servoB.attach(6);
  wristA.attach(9);
  wristB.attach(10);
  gripper.attach(11);
}

void writeAllCoupled(int angle) {
  baseServo.write(angle);

  // A1 y A2 acoplados
  servoA1.write(angle);
  servoA2.write(180 - angle);

  servoB.write(angle);
  wristA.write(angle);
  wristB.write(angle);
  gripper.write(angle);
}

void moveAllSmooth(int targetAngle, int stepDelayMs) {
  if (targetAngle > currentAngle) {
    for (int a = currentAngle; a <= targetAngle; a++) {
      writeAllCoupled(a);
      delay(stepDelayMs);
    }
  } else {
    for (int a = currentAngle; a >= targetAngle; a--) {
      writeAllCoupled(a);
      delay(stepDelayMs);
    }
  }

  currentAngle = targetAngle;
}

void setup() {
  attachAll();

  // Arranque seguro
  writeAllCoupled(currentAngle);
  delay(4000);
}

void loop() {
  moveAllSmooth(110, 40);
  delay(1500);

  moveAllSmooth(70, 40);
  delay(1500);

  moveAllSmooth(90, 40);
  delay(2000);
}