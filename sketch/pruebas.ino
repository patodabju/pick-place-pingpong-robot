#include <Servo.h>

Servo s;

void setup() {
  s.attach(8);   // 🔧 solo usamos el pin 9
}

void loop() {
  s.write(90);   // centro
  delay(2000);

  s.write(60);   // lado 1
  delay(2000);

  s.write(120);  // lado 2
  delay(2000);
}