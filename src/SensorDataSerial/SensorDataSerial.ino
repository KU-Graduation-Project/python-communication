#include <LSM6DS3.h>
#include <Wire.h>

//Create a instance of class LSM6DS3
LSM6DS3 myIMU(I2C_MODE, 0x6A);    //I2C device address 0x6A

#define CONVERT_TO_MS2    9.80665f
#define FREQUENCY_HZ        50
#define INTERVAL_MS         (1000 / (FREQUENCY_HZ + 1))

static unsigned long last_interval_ms = 0;               

void setup() {
    // put your setup code here, to run once:
    Serial.begin(9600);
    while (!Serial);
    //Call .begin() to configure the IMUs
    if (myIMU.begin() != 0) {
        Serial.println("Device error");
    } else {
        Serial.println("Device OK!");
    }
}

void loop() {

   if (millis() > last_interval_ms + INTERVAL_MS) {
        last_interval_ms = millis();
    //Accelerometer
    Serial.print(myIMU.readFloatAccelX() * CONVERT_TO_MS2,4);
    Serial.print('\t');
    Serial.print(myIMU.readFloatAccelY() * CONVERT_TO_MS2,4);
    Serial.print('\t');
    Serial.print(myIMU.readFloatAccelZ() * CONVERT_TO_MS2,4);
    Serial.print('\t');

    //Gyroscope
    Serial.print(myIMU.readFloatGyroX() * CONVERT_TO_MS2,4);
    Serial.print('\t');
    Serial.print(myIMU.readFloatGyroY() * CONVERT_TO_MS2,4);
    Serial.print('\t');
    Serial.print(myIMU.readFloatGyroZ() * CONVERT_TO_MS2,4);
    Serial.print('\t');                                

    //Thermometer
    Serial.println(myIMU.readTempC());
   }
}
