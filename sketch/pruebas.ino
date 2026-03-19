#include <Servo.h>

Servo s;

// 🔧 CAMBIA ESTE PIN para probar cada servo
const int SERVO_PIN = 3;

void setup() {
  s.attach(SERVO_PIN);
  s.write(90);   // centro
}

void loop() {
  // No hacemos nada, el servo se queda en 90°
}