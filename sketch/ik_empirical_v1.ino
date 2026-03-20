#include <Servo.h>
#include <math.h>

// =========================
// SERVOS
// =========================
Servo baseServo;   // pin 3
Servo servoA1;     // pin 4
Servo servoA2;     // pin 5 (mirror)
Servo servoB;      // pin 6
Servo wristA;      // pin 9
Servo wristB;      // pin 10
Servo gripper;     // pin 11

// =========================
// CONFIG
// =========================
const int WRISTA_FIXED = 90;
const int WRISTB_FIXED = 90;
const int GRIPPER_FIXED = 90;

// Movimiento lento: si antes usabas ~12-15, esto ya es mucho más lento
const int STEP_DELAY_MS = 60;

// Restricción dada
const int A1_MIN = 55;

// =========================
// POSICIONES ACTUALES
// =========================
int posBase = 90;
int posA1   = 90;
int posA2   = 90;
int posB    = 90;
int posWA   = 90;
int posWB   = 90;
int posGrip = 90;

// =========================
// DATOS DE CALIBRACIÓN
// Formato: x, y, base, a1, b
// Coordenadas en TU sistema de mesa
// =========================
struct Sample {
  float x;
  float y;
  float base;
  float a1;
  float b;
};

const int N = 10;
Sample samples[N] = {
  {  41,  20, 109, 122,  90},
  { 272, 150,  63, 105, 134},
  { 194, 138,  82, 105, 134},
  { 170, 130,  90, 114, 134},
  { 350, 245,  33, 101, 140},
  {  76,  86,  96, 111, 121},
  {  39, 180, 118, 103, 142},
  { 348,  59,  47, 121,  95},
  { 178, 229,  69,  96, 159},
  { 329, 101,  45, 114, 114}
};

// =========================
// UTILIDADES
// =========================
float dist2D(float x1, float y1, float x2, float y2) {
  float dx = x1 - x2;
  float dy = y1 - y2;
  return sqrt(dx * dx + dy * dy);
}

void moveSmooth(Servo &servo, int &currentPos, int target) {
  while (currentPos != target) {
    if (currentPos < target) currentPos++;
    else currentPos--;

    servo.write(currentPos);
    delay(STEP_DELAY_MS);
  }
}

void moveMirrorSmooth(int targetA1) {
  int targetA2 = 180 - targetA1;

  while (posA1 != targetA1 || posA2 != targetA2) {
    if (posA1 < targetA1) posA1++;
    else if (posA1 > targetA1) posA1--;

    if (posA2 < targetA2) posA2++;
    else if (posA2 > targetA2) posA2--;

    servoA1.write(posA1);
    servoA2.write(posA2);

    delay(STEP_DELAY_MS);
  }
}

// =========================
// IK EMPÍRICA POR INTERPOLACIÓN
// Usa 3 vecinos más cercanos con ponderación por distancia
// =========================
bool estimateAnglesFromXY(float x, float y, float &baseOut, float &a1Out, float &bOut) {
  int idx1 = -1, idx2 = -1, idx3 = -1;
  float d1 = 1e9, d2 = 1e9, d3 = 1e9;

  for (int i = 0; i < N; i++) {
    float d = dist2D(x, y, samples[i].x, samples[i].y);

    if (d < d1) {
      d3 = d2; idx3 = idx2;
      d2 = d1; idx2 = idx1;
      d1 = d;  idx1 = i;
    } else if (d < d2) {
      d3 = d2; idx3 = idx2;
      d2 = d;  idx2 = i;
    } else if (d < d3) {
      d3 = d;  idx3 = i;
    }
  }

  if (idx1 < 0 || idx2 < 0 || idx3 < 0) return false;

  // Si cae casi encima de un punto calibrado, úsalo directo
  if (d1 < 1.0) {
    baseOut = samples[idx1].base;
    a1Out   = samples[idx1].a1;
    bOut    = samples[idx1].b;
    return true;
  }

  // Pesos inversos a distancia
  float w1 = 1.0 / (d1 + 0.001);
  float w2 = 1.0 / (d2 + 0.001);
  float w3 = 1.0 / (d3 + 0.001);
  float ws = w1 + w2 + w3;

  baseOut = (w1 * samples[idx1].base + w2 * samples[idx2].base + w3 * samples[idx3].base) / ws;
  a1Out   = (w1 * samples[idx1].a1   + w2 * samples[idx2].a1   + w3 * samples[idx3].a1)   / ws;
  bOut    = (w1 * samples[idx1].b    + w2 * samples[idx2].b    + w3 * samples[idx3].b)    / ws;

  return true;
}

// =========================
// SETUP
// =========================
void setup() {
  Serial.begin(115200);

  baseServo.attach(3);
  servoA1.attach(4);
  servoA2.attach(5);
  servoB.attach(6);
  wristA.attach(9);
  wristB.attach(10);
  gripper.attach(11);

  // Estado inicial
  baseServo.write(posBase);
  servoA1.write(posA1);
  servoA2.write(posA2);
  servoB.write(posB);
  wristA.write(posWA);
  wristB.write(posWB);
  gripper.write(posGrip);

  // Fijar muñeca y gripper
  moveSmooth(wristA, posWA, WRISTA_FIXED);
  moveSmooth(wristB, posWB, WRISTB_FIXED);
  moveSmooth(gripper, posGrip, GRIPPER_FIXED);

  Serial.println("Listo.");
  Serial.println("Envia: x y");
  Serial.println("Ejemplo: 170 130");
}

// =========================
// LOOP
// =========================
void loop() {
  if (Serial.available() > 0) {
    float x = Serial.parseFloat();
    float y = Serial.parseFloat();

    while (Serial.available()) Serial.read();

    float targetBase, targetA1, targetB;

    bool ok = estimateAnglesFromXY(x, y, targetBase, targetA1, targetB);

    if (!ok) {
      Serial.println("Error calculando angulos.");
      return;
    }

    int baseCmd = constrain((int)round(targetBase), 0, 180);
    int a1Cmd   = constrain((int)round(targetA1), A1_MIN, 180);
    int bCmd    = constrain((int)round(targetB), 0, 180);

    Serial.print("XY: ");
    Serial.print(x); Serial.print(", ");
    Serial.print(y); Serial.print(" -> ");

    Serial.print("Base=");
    Serial.print(baseCmd);
    Serial.print(" A1=");
    Serial.print(a1Cmd);
    Serial.print(" A2=");
    Serial.print(180 - a1Cmd);
    Serial.print(" B=");
    Serial.println(bCmd);

    // Movimiento secuencial lento
    moveSmooth(baseServo, posBase, baseCmd);
    moveMirrorSmooth(a1Cmd);
    moveSmooth(servoB, posB, bCmd);

    // Muñeca/gripper se mantienen fijos
    moveSmooth(wristA, posWA, WRISTA_FIXED);
    moveSmooth(wristB, posWB, WRISTB_FIXED);
    moveSmooth(gripper, posGrip, GRIPPER_FIXED);

    Serial.println("Movimiento completado.");
  }
}