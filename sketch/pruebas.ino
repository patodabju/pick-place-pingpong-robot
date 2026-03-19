#include <Servo.h>

Servo A1;
Servo A2;

void setup() {
  A1.attach(4);   // 🔧 cambia si tu A1 está en otro pin
  A2.attach(5);   // 🔧 cambia si tu A2 está en otro pin
}

void loop() {
  // Centro
  A1.write(90);
  A2.write(90);
  delay(2000);

  // Movimiento hacia un lado
  A1.write(60);
  A2.write(120);   // 🔥 esclavizado inverso
  delay(2000);

  // Movimiento hacia el otro lado
  A1.write(120);
  A2.write(60);    // 🔥 esclavizado inverso
  delay(2000);
}