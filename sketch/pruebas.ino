void setup() {
  pinMode(9, OUTPUT);   // 🔧 usa el pin 9 (Wrist A por ejemplo)
}

void loop() {
  // 🔵 Centro (~90°)
  digitalWrite(9, HIGH);
  delayMicroseconds(1500);
  digitalWrite(9, LOW);
  delayMicroseconds(18500);
  delay(2000);

  // 🔴 Lado 1 (~60°)
  digitalWrite(9, HIGH);
  delayMicroseconds(1200);
  digitalWrite(9, LOW);
  delayMicroseconds(18800);
  delay(2000);

  // 🟢 Lado 2 (~120°)
  digitalWrite(9, HIGH);
  delayMicroseconds(1800);
  digitalWrite(9, LOW);
  delayMicroseconds(18200);
  delay(2000);
}