#include <Arduino.h>
#include <HardwareSerial.h>
HardwareSerial co2_serial(2); // RX2 = pin IO16, TX2 = pin IO17

unsigned char hexdata[9] = {0xFF, 0x01, 0x86, 0x00, 0x00, 0x00, 0x00, 0x00, 0x79}; //Read the gas density command /Don't change the order
void setup()
{

    Serial.begin(9600);
    while (!Serial)
    {
        delay(1);
    }
    co2_serial.begin(9600);
}

void loop()
{
    co2_serial.write(hexdata, 9);
    delay(500);

    for (int i = 0, j = 0; i < 9; i++) {
        if (co2_serial.available() > 0) {
            long hi, lo, CO2;
            int ch = co2_serial.read();

            if (i == 2) {
                hi = ch;
            } //High concentration
            if (i == 3) {
                lo = ch;
            } //Low concentration
            if (i == 8) {
                CO2 = hi * 256 + lo; //CO2 concentration
                Serial.print("CO2 concentration: ");
                Serial.print(CO2);
                Serial.println("ppm");
            }
        }
    }
}