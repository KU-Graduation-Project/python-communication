
#include <ArduinoBLE.h>
#include <LSM6DS3.h>
#include <Wire.h>

#define CONVERT_TO_MS2    9.80665f
#define MAX_ACCEPTED_RANGE  2.0f

#define FREQUENCY_HZ        20
#define INTERVAL_MS         (10000 / (FREQUENCY_HZ + 1))
static unsigned long last_interval_ms = 0;     

LSM6DS3 myIMU(I2C_MODE, 0x6A);
static bool debug_nn = false;

BLEService myService("ffff");
BLEShortCharacteristic accelerometerCharacteristic_X("ffa1", BLERead | BLEBroadcast | BLENotify);
BLEShortCharacteristic accelerometerCharacteristic_Y("ffa2", BLERead | BLEBroadcast | BLENotify);
BLEShortCharacteristic accelerometerCharacteristic_Z("ffa3", BLERead | BLEBroadcast | BLENotify);
BLEShortCharacteristic gyroscopeCharacteristic_X("ffb1", BLERead | BLEBroadcast | BLENotify);
BLEShortCharacteristic gyroscopeCharacteristic_Y("ffb2", BLERead | BLEBroadcast | BLENotify);
BLEShortCharacteristic gyroscopeCharacteristic_Z("ffb3", BLERead | BLEBroadcast | BLENotify);
BLEShortCharacteristic temperatureCharacteristic("ffc1", BLERead | BLEBroadcast | BLENotify);

// Bluetooth® Low Energy Battery Level Characteristic
BLEUnsignedCharCharacteristic batteryLevelCharacteristic("2A19", BLERead | BLEBroadcast | BLENotify);


void setup() {
  Serial.begin(9600);
  
  BLE.begin();
  myIMU.begin();

   BLE.setLocalName("Test sensor");
   
  myService.addCharacteristic(accelerometerCharacteristic_X);
  myService.addCharacteristic(accelerometerCharacteristic_Y);
  myService.addCharacteristic(accelerometerCharacteristic_Z);
  myService.addCharacteristic(gyroscopeCharacteristic_X);
  myService.addCharacteristic(gyroscopeCharacteristic_Y);
  myService.addCharacteristic(gyroscopeCharacteristic_Z);
  myService.addCharacteristic(temperatureCharacteristic);
  myService.addCharacteristic(batteryLevelCharacteristic);
  accelerometerCharacteristic_X.writeValue(0);
  accelerometerCharacteristic_Y.writeValue(0);
  accelerometerCharacteristic_Z.writeValue(0);
  gyroscopeCharacteristic_X.writeValue(0);
  gyroscopeCharacteristic_Y.writeValue(0);
  gyroscopeCharacteristic_Z.writeValue(0);
  temperatureCharacteristic.writeValue(0);
  batteryLevelCharacteristic.writeValue(0);
   
  BLE.addService(myService);

  BLE.advertise();

}

void loop() {
  BLEDevice central = BLE.central();

  if(central.connected()){
    digitalWrite(LED_BUILTIN, HIGH);
  }

  const uint32_t BLE_UPDATE_INTERVAL = 2;
  static uint32_t previousMillis = 0;
  uint32_t currentMillis = millis();
  

   if (millis() > last_interval_ms + INTERVAL_MS) {
    last_interval_ms = millis();
    BLE.poll();
  }

  
   int16_t accelerometer_X = round(myIMU.readFloatAccelX() * 100.0);
   int16_t accelerometer_Y = round(myIMU.readFloatAccelY() * 100.0);
   int16_t accelerometer_Z = round(myIMU.readFloatAccelZ() * 100.0);
   int16_t gyroscope_X = round(myIMU.readFloatGyroX() * 100.0);
   int16_t gyroscope_Y = round(myIMU.readFloatGyroY() * 100.0);
   int16_t gyroscope_Z = round(myIMU.readFloatGyroZ() * 100.0);
   int16_t temperature = round(myIMU.readTempC() * 100.0);

   int battery = analogRead(A0);
   int batteryLevel = map(battery, 0, 1023, 0, 100);


   if(accelerometerCharacteristic_X.writeValue(accelerometer_X)){

    Serial.println("BLE write");
   }
   accelerometerCharacteristic_Y.writeValue(accelerometer_Y);
   accelerometerCharacteristic_Z.writeValue(accelerometer_Z);
   gyroscopeCharacteristic_X.writeValue(gyroscope_X);
   gyroscopeCharacteristic_Y.writeValue(gyroscope_Y);
   gyroscopeCharacteristic_Z.writeValue(gyroscope_Z);
   temperatureCharacteristic.writeValue(temperature);
   batteryLevelCharacteristic.writeValue(batteryLevel);


}
