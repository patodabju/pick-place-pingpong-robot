#include <Servo.h>

// Servos
Servo baseServo;     // pin 3
Servo servoA1;       // pin 4
Servo servoA2;       // pin 5
Servo servoB;        // pin 6
Servo wristA;        // pin 9
Servo wristB;        // pin 10
Servo gripper;       // pin 11

void attachAll() {
  baseServo.attach(3);
  servoA1.attach(4);
  servoA2.attach(5);
  servoB.attach(6);
  wristA.attach(9);
  wristB.attach(10);
  gripper.attach(11);
}

// Función para mover todo
void moveAll(int angle) {

  // Base
  baseServo.write(angle);

  // 🔥 A1 y A2 acoplados
  servoA1.write(angle);
  servoA2.write(180 - angle);

  // Resto
  servoB.write(angle);
  wristA.write(angle);
  wristB.write(angle);
  gripper.write(angle);
}

void setup() {
  attachAll();

  // Centro inicial
  moveAll(90);
  delay(3000);
}

void loop() {

  // +20°
  moveAll(110);
  delay(3000);

  // -20°
  moveAll(70);
  delay(3000);

  // Centro
  moveAll(90);
  delay(3000);
}