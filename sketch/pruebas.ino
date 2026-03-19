void setup() {
  pinMode(9, OUTPUT);
}

void loop() {
  digitalWrite(9, HIGH);
  delayMicroseconds(1500);   // centro aproximado
  digitalWrite(9, LOW);
  delayMicroseconds(18500);  // periodo total ~20 ms
}