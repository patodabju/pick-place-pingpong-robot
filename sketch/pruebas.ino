int pins[] = {3, 4, 5, 6, 9, 10, 11};  // tus servos
int numServos = 7;

int pulse = 1500;
int target = 1500;

void setup() {
  for (int i = 0; i < numServos; i++) {
    pinMode(pins[i], OUTPUT);
  }

  randomSeed(analogRead(0));  // para random real
}

void loop() {

  for (int i = 0; i < numServos; i++) {

    // elegir posición aleatoria (1000 a 2000 us)
    target = random(1000, 2000);

    // mantener señal por un rato (para que el servo llegue)
    for (int t = 0; t < 80; t++) {

      digitalWrite(pins[i], HIGH);
      delayMicroseconds(target);
      digitalWrite(pins[i], LOW);
      delayMicroseconds(20000 - target);
    }

    delay(500); // pausa entre servos
  }
}