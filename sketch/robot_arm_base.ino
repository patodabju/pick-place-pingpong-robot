#include <Servo.h>

// Servos
Servo baseServo;   // pin 3
Servo servoA1;     // pin 4
Servo servoA2;     // pin 5
Servo servoB;      // pin 6
Servo wristA;      // pin 9
Servo wristB;      // pin 10
Servo gripper;     // pin 11

// ========= CONFIGURACIÓN =========
// Posición inicial "contraída" o de arranque.
// Ajústala si ves que 60 fuerza demasiado algún joint.
const int START_ANGLE = 60;

// Centro deseado
const int CENTER_ANGLE = 90;

// Delay entre movimientos
const int WAIT_MS = 2000;

// =================================

void attachAll() {
  baseServo.attach(3);
  servoA1.attach(4);
  servoA2.attach(5);
  servoB.attach(6);
  wristA.attach(9);
  wristB.attach(10);
  gripper.attach(11);
}

void goToStartPosition() {
  baseServo.write(START_ANGLE);

  // A1 y A2 acoplados
  servoA1.write(START_ANGLE);
  servoA2.write(180 - START_ANGLE);

  servoB.write(START_ANGLE);
  wristA.write(START_ANGLE);
  wristB.write(START_ANGLE);
  gripper.write(START_ANGLE);
}

void setup() {
  attachAll();

  // Llevar todo a posición inicial
  goToStartPosition();
  delay(4000);
}

void loop() {
  // 1) Base a 90
  baseServo.write(CENTER_ANGLE);
  delay(WAIT_MS);

  // 2) A1 y A2 a 90 acoplados
  servoA1.write(CENTER_ANGLE);
  servoA2.write(180 - CENTER_ANGLE);
  delay(WAIT_MS);

  // 3) B a 90
  servoB.write(CENTER_ANGLE);
  delay(WAIT_MS);

  // 4) Wrist A a 90
  wristA.write(CENTER_ANGLE);
  delay(WAIT_MS);

  // 5) Wrist B a 90
  wristB.write(CENTER_ANGLE);
  delay(WAIT_MS);

  // 6) Gripper a 90
  gripper.write(CENTER_ANGLE);
  delay(WAIT_MS);

  // Espera extra al final
  delay(3000);

  // Repetir ciclo: volver a posición inicial
  goToStartPosition();
  delay(4000);
}