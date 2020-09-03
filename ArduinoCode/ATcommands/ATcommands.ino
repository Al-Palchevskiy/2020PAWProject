/*
  Blink
  Turns on an LED on for one second, then off for one second, repeatedly.

  This example code is in the public domain.
 */

// Pin 13 has an LED connected on most Arduino boards.
// Pin 11 has the LED on Teensy 2.0
// Pin 6  has the LED on Teensy++ 2.0
// Pin 13 has the LED on Teensy 3.0
// give it a name:
int led = 13;

// the setup routine runs once when you press reset:
void setup() {
  // initialize the digital pin as an output.
  pinMode(led, OUTPUT);
  Serial.begin(38400);
  Serial1.begin(38400);
}

// the loop routine runs over and over again forever:
void loop() {
  
  //Serial.write("AT\r\n");
  //Serial1.write("AT+ORGL\r\n");
  //readSerial();
  //Serial1.write("AT+NAME=HC-05-RIGHT\r\n");
  //readSerial();
  Serial1.write("AT+NAME?\r\n");
  readSerial();
  Serial1.write("AT+ADDR?\r\n");
  readSerial();
  Serial1.write("AT+ROLE?\r\n");
  readSerial();
  Serial1.write("AT+CMODE?\r\n");
  readSerial();
  Serial1.write("AT+BIND?\r\n");
  readSerial();
  Serial1.write("AT+PSWD?\r\n");
  readSerial();
  Serial1.write("AT+UART?\r\n");
  readSerial();
  Serial1.write("AT+CLASS?\r\n");
  readSerial();
  Serial1.write("AT+ADCN?\r\n");
  readSerial();
  Serial1.write("AT+VERSION?\r\n");
  readSerial();
  //Serial1.write("AT+UART:230400,0,0\r\n");
  readSerial();
  
  //Serial.write("ENTER");
  
  while (true) {
    digitalWrite(led, HIGH);   // turn the LED on (HIGH is the voltage level)
    delay(500);               // wait for a second
    digitalWrite(led, LOW);    // turn the LED off by making the voltage LOW
    delay(500);               // wait for a second
    readSerial();
//    while (Serial.available()) {      // If anything comes in Serial (USB),
//      Serial.write(Serial.read());   // read it and send it out Serial1 (pins 0 & 1)
//    }
    
    
  }
  }
  void readSerial() {
    delay(1000);
    while (Serial1.available()) {     // If anything comes in Serial1 (pins 0 & 1)
      Serial.write(Serial1.read());   // read it and send it out Serial (USB)
    }

  }
  
  
  
