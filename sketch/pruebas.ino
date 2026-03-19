void setup() {
  pinMode(3, OUTPUT);
}

void loop() {
  // Pulso ~1.5 ms (posición media)
  digitalWrite(3, HIGH);
  delayMicroseconds(1500);
  digitalWrite(3, LOW);

  // Periodo total 20 ms
  delay(20);
}