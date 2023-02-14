#include <ArduinoBLE.h>
#include <LSM6DS3.h>
#include <Wire.h>

#define CONVERT_TO_MS2    9.80665f
#define MAX_ACCEPTED_RANGE  2.0f

LSM6DS3 myIMU(I2C_MODE, 0x6A);
static bool debug_nn = false;

BLEService myService("fff0");
BLEShortCharacteristic accelerometerCharacteristic_X("ffa1", BLERead | BLEBroadcast);
BLEShortCharacteristic accelerometerCharacteristic_Y("ffa2", BLERead | BLEBroadcast);
BLEShortCharacteristic accelerometerCharacteristic_Z("ffa3", BLERead | BLEBroadcast);
BLEShortCharacteristic gyroscopeCharacteristic_X("ffb1", BLERead | BLEBroadcast);
BLEShortCharacteristic gyroscopeCharacteristic_Y("ffb2", BLERead | BLEBroadcast);
BLEShortCharacteristic gyroscopeCharacteristic_Z("ffb3", BLERead | BLEBroadcast);


void setup() {
  BLE.begin();
  myIMU.begin();

   BLE.setLocalName("Test sensor");
   
  myService.addCharacteristic(accelerometerCharacteristic_X);
  myService.addCharacteristic(accelerometerCharacteristic_Y);
  myService.addCharacteristic(accelerometerCharacteristic_Z);
  myService.addCharacteristic(gyroscopeCharacteristic_X);
  myService.addCharacteristic(gyroscopeCharacteristic_Y);
  myService.addCharacteristic(gyroscopeCharacteristic_Z);
  accelerometerCharacteristic_X.writeValue(0);
  accelerometerCharacteristic_Y.writeValue(0);
  accelerometerCharacteristic_Z.writeValue(0);
  gyroscopeCharacteristic_X.writeValue(0);
  gyroscopeCharacteristic_Y.writeValue(0);
  gyroscopeCharacteristic_Z.writeValue(0);
   
  BLE.addService(myService);

  BLE.advertise();

}

void loop() {
  BLEDevice central = BLE.central();

  if(central.connected()){
    digitalWrite(LED_BUILTIN, HIGH);
  }

  const uint32_t BLE_UPDATE_INTERVAL = 10;
  static uint32_t previousMillis = 0;
  uint32_t currentMillis = millis();
  
  if (currentMillis - previousMillis >= BLE_UPDATE_INTERVAL) {
    previousMillis = currentMillis;
    BLE.poll();
  }
  
   int16_t accelerometer_X = round(myIMU.readFloatAccelX() * 100.0);
   int16_t accelerometer_Y = round(myIMU.readFloatAccelY() * 100.0);
   int16_t accelerometer_Z = round(myIMU.readFloatAccelZ() * 100.0);
   int16_t gyroscope_X = round(myIMU.readFloatGyroX() * 100.0);
   int16_t gyroscope_Y = round(myIMU.readFloatGyroY() * 100.0);
   int16_t gyroscope_Z = round(myIMU.readFloatGyroZ() * 100.0);

   
   accelerometerCharacteristic_X.writeValue(accelerometer_X);
   accelerometerCharacteristic_Y.writeValue(accelerometer_Y);
   accelerometerCharacteristic_Z.writeValue(accelerometer_Z);
   gyroscopeCharacteristic_X.writeValue(gyroscope_X);
   gyroscopeCharacteristic_Y.writeValue(gyroscope_Y);
   gyroscopeCharacteristic_Z.writeValue(gyroscope_Z);


}
