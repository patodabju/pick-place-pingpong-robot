/*
  robot_arm_base.ino

  Firmware base para brazo robótico con 7 servos físicos
  y 6 variables de control recibidas por puerto serial.

  Formato serial:
    SET,90,90,90,90,90,90
    HOME
    STATUS
    HELP

  Variables de control recibidas:
    0 -> Root
    1 -> Arm A1
    2 -> Arm B
    3 -> Wrist A
    4 -> Wrist B
    5 -> Gripper

  Servos físicos:
    servo 0 -> Root
    servo 1 -> Arm A1
    servo 2 -> Arm A2   (esclavo de Arm A1)
    servo 3 -> Arm B
    servo 4 -> Wrist A
    servo 5 -> Wrist B
    servo 6 -> Gripper
*/

#include <Servo.h>
#include <string.h>
#include <stdlib.h>

const uint8_t NUM_CMD = 6;
const uint8_t NUM_SERVOS = 7;

// Pines físicos de servos
const uint8_t servoPins[NUM_SERVOS] = {3, 4, 5, 6, 9, 10, 11};

// Objetos servo
Servo servos[NUM_SERVOS];

// Nombres para depuración
const char* cmdNames[NUM_CMD] = {
  "Root", "ArmA1", "ArmB", "WristA", "WristB", "Gripper"
};

const char* servoNames[NUM_SERVOS] = {
  "Root", "ArmA1", "ArmA2", "ArmB", "WristA", "WristB", "Gripper"
};

// Estado actual de los 6 comandos de entrada
int cmdAngles[NUM_CMD] = {90, 90, 90, 90, 90, 90};

// Estado actual real de los 7 servos
int currentServoAngles[NUM_SERVOS] = {90, 90, 90, 90, 90, 90, 90};

// Posición HOME inicial
int homeCmdAngles[NUM_CMD] = {90, 90, 90, 90, 90, 90};

// Límites para las 6 variables de entrada
int cmdMin[NUM_CMD] = {  0,  15,  15,   0,   0,  10};
int cmdMax[NUM_CMD] = {180, 165, 165, 180, 180, 110};

// Límites para los 7 servos físicos
int servoMin[NUM_SERVOS] = {  0,  15,  15,  15,   0,   0,  10};
int servoMax[NUM_SERVOS] = {180, 165, 165, 165, 180, 180, 110};

// Buffer serial
const uint16_t SERIAL_BUFFER_SIZE = 96;
char serialBuffer[SERIAL_BUFFER_SIZE];

// --------------------------------------------------
// Utilidades
// --------------------------------------------------
int clampInt(int value, int minVal, int maxVal) {
  if (value < minVal) return minVal;
  if (value > maxVal) return maxVal;
  return value;
}

void printHelp() {
  Serial.println(F("=== COMANDOS DISPONIBLES ==="));
  Serial.println(F("SET,a0,a1,a2,a3,a4,a5"));
  Serial.println(F("  a0 = Root"));
  Serial.println(F("  a1 = ArmA1"));
  Serial.println(F("  a2 = ArmB"));
  Serial.println(F("  a3 = WristA"));
  Serial.println(F("  a4 = WristB"));
  Serial.println(F("  a5 = Gripper"));
  Serial.println(F("HOME"));
  Serial.println(F("STATUS"));
  Serial.println(F("HELP"));
  Serial.println(F("Ejemplo:"));
  Serial.println(F("SET,90,90,90,90,90,90"));
  Serial.println();
}

void printStatus() {
  Serial.println(F("=== STATUS ==="));

  Serial.println(F("Comandos actuales (6):"));
  for (uint8_t i = 0; i < NUM_CMD; i++) {
    Serial.print(cmdNames[i]);
    Serial.print(F(": "));
    Serial.println(cmdAngles[i]);
  }

  Serial.println(F("Servos físicos (7):"));
  for (uint8_t i = 0; i < NUM_SERVOS; i++) {
    Serial.print(servoNames[i]);
    Serial.print(F(": "));
    Serial.println(currentServoAngles[i]);
  }

  Serial.println();
}

// --------------------------------------------------
// Conversión 6 comandos -> 7 servos
// --------------------------------------------------
void computeServoTargetsFromCmd(const int inputCmd[NUM_CMD], int outServoAngles[NUM_SERVOS]) {
  outServoAngles[0] = inputCmd[0];       // Root
  outServoAngles[1] = inputCmd[1];       // Arm A1
  outServoAngles[2] = 180 - inputCmd[1]; // Arm A2 esclavo
  outServoAngles[3] = inputCmd[2];       // Arm B
  outServoAngles[4] = inputCmd[3];       // Wrist A
  outServoAngles[5] = inputCmd[4];       // Wrist B
  outServoAngles[6] = inputCmd[5];       // Gripper

  for (uint8_t i = 0; i < NUM_SERVOS; i++) {
    outServoAngles[i] = clampInt(outServoAngles[i], servoMin[i], servoMax[i]);
  }
}

// --------------------------------------------------
// Movimiento
// --------------------------------------------------
void writeServos(const int targetServoAngles[NUM_SERVOS]) {
  for (uint8_t i = 0; i < NUM_SERVOS; i++) {
    servos[i].write(targetServoAngles[i]);
    currentServoAngles[i] = targetServoAngles[i];
  }
}

void applyCommandAngles(const int newCmdAngles[NUM_CMD]) {
  for (uint8_t i = 0; i < NUM_CMD; i++) {
    cmdAngles[i] = clampInt(newCmdAngles[i], cmdMin[i], cmdMax[i]);
  }

  int targetServoAngles[NUM_SERVOS];
  computeServoTargetsFromCmd(cmdAngles, targetServoAngles);
  writeServos(targetServoAngles);
}

void goHome() {
  applyCommandAngles(homeCmdAngles);
  Serial.println(F("OK: HOME"));
}

// --------------------------------------------------
// Parser serial
// --------------------------------------------------
bool parseSetCommand(char* line, int outAngles[NUM_CMD]) {
  char* token = strtok(line, ",");

  if (token == NULL) return false;
  if (strcmp(token, "SET") != 0) return false;

  for (uint8_t i = 0; i < NUM_CMD; i++) {
    token = strtok(NULL, ",");
    if (token == NULL) return false;
    outAngles[i] = atoi(token);
  }

  return true;
}

void handleSerialCommand(char* line) {
  if (strlen(line) == 0) return;

  char temp[SERIAL_BUFFER_SIZE];
  strncpy(temp, line, SERIAL_BUFFER_SIZE - 1);
  temp[SERIAL_BUFFER_SIZE - 1] = '\0';

  if (strcmp(temp, "HOME") == 0) {
    goHome();
    return;
  }

  if (strcmp(temp, "STATUS") == 0) {
    printStatus();
    return;
  }

  if (strcmp(temp, "HELP") == 0) {
    printHelp();
    return;
  }

  int parsedAngles[NUM_CMD];
  if (parseSetCommand(temp, parsedAngles)) {
    applyCommandAngles(parsedAngles);

    Serial.print(F("OK: SET -> "));
    for (uint8_t i = 0; i < NUM_CMD; i++) {
      Serial.print(cmdAngles[i]);
      if (i < NUM_CMD - 1) Serial.print(',');
    }
    Serial.println();
    return;
  }

  Serial.println(F("ERROR: comando invalido. Usa HELP"));
}

void readSerialLine() {
  static uint16_t idx = 0;

  while (Serial.available() > 0) {
    char c = Serial.read();

    if (c == '\r') {
      continue;
    }

    if (c == '\n') {
      serialBuffer[idx] = '\0';
      handleSerialCommand(serialBuffer);
      idx = 0;
      return;
    }

    if (idx < SERIAL_BUFFER_SIZE - 1) {
      serialBuffer[idx++] = c;
    } else {
      serialBuffer[idx] = '\0';
      Serial.println(F("ERROR: linea demasiado larga"));
      idx = 0;
      return;
    }
  }
}

// --------------------------------------------------
// Setup / Loop
// --------------------------------------------------
void setup() {
  Serial.begin(9600);
  delay(500);

  for (uint8_t i = 0; i < NUM_SERVOS; i++) {
    servos[i].attach(servoPins[i]);
  }

  goHome();

  Serial.println(F("Brazo robot listo."));
  printHelp();
}

void loop() {
  readSerialLine();
}