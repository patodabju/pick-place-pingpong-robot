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

void testServo(Servo &s) {
  s.write(90);
  delay(1000);

  s.write(80);
  delay(1000);
  s.write(90);
  delay(1000);

  s.write(100);
  delay(1000);
  s.write(90);
  delay(1000);
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
  delay(4000);
}

void loop() {
  testServo(servo1);
  testServo(servo2);
  testServo(servo3);
  testServo(servo4);
  testServo(servo5);
  testServo(servo6);
  testServo(servo7);

  delay(2000);
}