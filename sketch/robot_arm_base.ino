#include <Servo.h>

Servo s1, s2, s3, s4, s5, s6, s7;

// Pines
const int pins[7] = {3, 4, 5, 6, 9, 10, 11};

// Índices para claridad
#define BASE 0
#define A1   1
#define A2   2
#define B    3
#define W1   4
#define W2   5
#define GRIP 6

void attachAll() {
  s1.attach(pins[BASE]);
  s2.attach(pins[A1]);
  s3.attach(pins[A2]);
  s4.attach(pins[B]);
  s5.attach(pins[W1]);
  s6.attach(pins[W2]);
  s7.attach(pins[GRIP]);
}

void moveAll(int angle) {
  // Base
  s1.write(angle);

  // 🔥 A1 y A2 acoplados (espejo)
  s2.write(angle);           // A1
  s3.write(180 - angle);     // A2

  // Resto
  s4.write(angle);
  s5.write(angle);
  s6.write(angle);
  s7.write(angle);
}

void setup() {
  attachAll();

  // Centro
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