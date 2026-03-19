#include <Servo.h>

Servo s;

// 🔧 CAMBIA ESTE PIN para probar cada servo
const int SERVO_PIN = 3;

int angle = 90;

void setup() {
  Serial.begin(9600);
  s.attach(SERVO_PIN);

  s.write(angle);

  Serial.println("Servo listo.");
  Serial.println("Escribe un angulo entre 0 y 180:");
}

void loop() {
  if (Serial.available()) {
    int newAngle = Serial.parseInt();

    // Validación básica
    if (newAngle >= 0 && newAngle <= 180) {
      angle = newAngle;
      s.write(angle);

      Serial.print("Moviendo a: ");
      Serial.println(angle);
    } else {
      Serial.println("Angulo invalido (0-180)");
    }
  }
}