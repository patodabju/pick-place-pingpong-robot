int pins[] = {2,3,4,5,6,7,8,9,10,11,12,13};

void setup() {
  for (int i = 0; i < 12; i++) {
    pinMode(pins[i], OUTPUT);
  }
}

void loop() {
  for (int i = 0; i < 12; i++) {

    // generar señal servo en ese pin
    for (int j = 0; j < 100; j++) {
      digitalWrite(pins[i], HIGH);
      delayMicroseconds(1500);
      digitalWrite(pins[i], LOW);
      delay(20);
    }

    delay(1000); // pausa entre pines
  }
}