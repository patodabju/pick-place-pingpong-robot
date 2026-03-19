#include <Servo.h>

Servo servoA1;
Servo servoA2;

void setup() {
  servoA1.attach(4);   // cambia si A1 está en otro pin
  servoA2.attach(5);   // cambia si A2 está en otro pin
}

void loop() {
  // Centro
  servoA1.write(90);
  servoA2.write(90);
  delay(2000);

  // Movimiento hacia un lado
  servoA1.write(60);
  servoA2.write(120);   // esclavizado inverso
  delay(2000);

  // Movimiento hacia el otro lado
  servoA1.write(120);
  servoA2.write(60);    // esclavizado inverso
  delay(2000);
}