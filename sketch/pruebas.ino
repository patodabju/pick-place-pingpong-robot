#include <Servo.h>

Servo servo1;
Servo servo2;
Servo servo3;
Servo servo4;
Servo servo5;
Servo servo6;
Servo servo7;

const int servoPins[7] = {3, 4, 5, 6, 9, 10, 11};

void centerAll() {
  servo1.write(90);
  servo2.write(90);
  servo3.write(90);
  servo4.write(90);
  servo5.write(90);
  servo6.write(90);
  servo7.write(90);
}

void setup() {
  servo1.attach(servoPins[0]);
  servo2.attach(servoPins[1]);
  servo3.attach(servoPins[2]);
  servo4.attach(servoPins[3]);
  servo5.attach(servoPins[4]);
  servo6.attach(servoPins[5]);
  servo7.attach(servoPins[6]);

  centerAll();
  delay(3000);
}

void loop() {
  // Servo 1
  servo1.write(75);
  delay(1200);
  servo1.write(105);
  delay(1200);
  servo1.write(90);
  delay(800);

  // Servo 2
  servo2.write(75);
  delay(1200);
  servo2.write(105);
  delay(1200);
  servo2.write(90);
  delay(800);

  // Servo 3
  servo3.write(75);
  delay(1200);
  servo3.write(105);
  delay(1200);
  servo3.write(90);
  delay(800);

  // Servo 4
  servo4.write(75);
  delay(1200);
  servo4.write(105);
  delay(1200);
  servo4.write(90);
  delay(800);

  // Servo 5
  servo5.write(75);
  delay(1200);
  servo5.write(105);
  delay(1200);
  servo5.write(90);
  delay(800);

  // Servo 6
  servo6.write(75);
  delay(1200);
  servo6.write(105);
  delay(1200);
  servo6.write(90);
  delay(800);

  // Servo 7
  servo7.write(75);
  delay(1200);
  servo7.write(105);
  delay(1200);
  servo7.write(90);
  delay(800);

  delay(2000);
}