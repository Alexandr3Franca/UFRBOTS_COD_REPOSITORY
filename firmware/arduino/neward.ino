#include <SoftwareSerial.h>

SoftwareSerial bluetooth(2, 3); // RX, TX

// Pinos do L298N
const int pinoEna = 11;
const int pinoEnb = 11;
const int pinoIn1 = 5;
const int pinoIn2 = 6;
const int pinoIn3 = 9;
const int pinoIn4 = 10;

void setup() {
  bluetooth.begin(9600);
  pinMode(pinoEna, OUTPUT);
  pinMode(pinoEnb, OUTPUT);
  pinMode(pinoIn1, OUTPUT);
  pinMode(pinoIn2, OUTPUT);
  pinMode(pinoIn3, OUTPUT);
  pinMode(pinoIn4, OUTPUT);

  // velocidade inicial = 0
  analogWrite(pinoEna, 0);
  analogWrite(pinoEnb, 0);
}

void loop() {
  if (bluetooth.available() > 0) {
    // Lê até encontrar '\n' (enviado pelo Python)
    String comando = bluetooth.readStringUntil('\n');

    if (comando.length() > 0) {
      char direcao = comando.charAt(0);           // ex: 'F'
      int velocidade = comando.substring(1).toInt(); // ex: "5" → 5

      // Escala 0–9 (do Python) para 0–255 (PWM do Arduino)
      int pwm = map(velocidade, 0, 9, 0, 255);

      switch (direcao) {
        case 'F': // Frente
          analogWrite(pinoEna, pwm);
          analogWrite(pinoEnb, pwm);
          digitalWrite(pinoIn1, HIGH); digitalWrite(pinoIn2, LOW);
          digitalWrite(pinoIn3, HIGH); digitalWrite(pinoIn4, LOW);
          break;

        case 'B': // Trás
          analogWrite(pinoEna, pwm);
          analogWrite(pinoEnb, pwm);
          digitalWrite(pinoIn1, LOW); digitalWrite(pinoIn2, HIGH);
          digitalWrite(pinoIn3, LOW); digitalWrite(pinoIn4, HIGH);
          break;

        case 'L': // Esquerda
          analogWrite(pinoEna, pwm);
          analogWrite(pinoEnb, pwm);
          digitalWrite(pinoIn1, LOW); digitalWrite(pinoIn2, HIGH);
          digitalWrite(pinoIn3, HIGH); digitalWrite(pinoIn4, LOW);
          break;

        case 'R': // Direita
          analogWrite(pinoEna, pwm);
          analogWrite(pinoEnb, pwm);
          digitalWrite(pinoIn1, HIGH); digitalWrite(pinoIn2, LOW);
          digitalWrite(pinoIn3, LOW); digitalWrite(pinoIn4, HIGH);
          break;

        default: // Parado
          analogWrite(pinoEna, 0);
          analogWrite(pinoEnb, 0);
          digitalWrite(pinoIn1, LOW); digitalWrite(pinoIn2, LOW);
          digitalWrite(pinoIn3, LOW); digitalWrite(pinoIn4, LOW);
          break;
      }
    }
  }
}
