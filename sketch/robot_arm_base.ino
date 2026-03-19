#include <Servo.h>

Servo servo1;
Servo servo2;
Servo servo3;
Servo servo4;
Servo servo5;
Servo servo6;
Servo servo7;

const int servoPins[7] = {3, 4, 5, 6, 9, 10, 11};

void moveAll(int angle) {
  servo1.write(angle);
  servo2.write(angle);
  servo3.write(angle);
  servo4.write(angle);
  servo5.write(angle);
  servo6.write(angle);
  servo7.write(angle);
}

void setup() {
  servo1.attach(servoPins[0]);
  servo2.attach(servoPins[1]);
  servo3.attach(servoPins[2]);
  servo4.attach(servoPins[3]);
  servo5.attach(servoPins[4]);
  servo6.attach(servoPins[5]);
  servo7.attach(servoPins[6]);

  // Todos al centro
  moveAll(90);
  delay(3000);
}

void loop() {
  // +30° (máximo seguro)
  moveAll(120);
  delay(3000);

  // -30°
  moveAll(60);
  delay(3000);

  // Regresar a centro
  moveAll(90);
  delay(3000);
}