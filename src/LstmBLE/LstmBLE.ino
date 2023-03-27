
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
BLEShortCharacteristic temperatureCharacteristic("ffc1", BLERead | BLEBroadcast);


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
  myService.addCharacteristic(temperatureCharcteristic);
  accelerometerCharacteristic_X.writeValue(0);
  accelerometerCharacteristic_Y.writeValue(0);
  accelerometerCharacteristic_Z.writeValue(0);
  gyroscopeCharacteristic_X.writeValue(0);
  gyroscopeCharacteristic_Y.writeValue(0);
  gyroscopeCharacteristic_Z.writeValue(0);
  temperatureCharacteristic.writeValue(0);
   
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
  
  /*
  if (currentMillis - previousMillis >= BLE_UPDATE_INTERVAL) {
    previousMillis = currentMillis;
    BLE.poll();
  }
  */
  
   /*
   int16_t accelerometer_X = round(myIMU.readFloatAccelX() * 100.0);
   int16_t accelerometer_Y = round(myIMU.readFloatAccelY() * 100.0);
   int16_t accelerometer_Z = round(myIMU.readFloatAccelZ() * 100.0);
   int16_t gyroscope_X = round(myIMU.readFloatGyroX() * 100.0);
   int16_t gyroscope_Y = round(myIMU.readFloatGyroY() * 100.0);
   int16_t gyroscope_Z = round(myIMU.readFloatGyroZ() * 100.0);
   int16_t temperature = round(myIMU.readTemperature() * 100.0);

   
   accelerometerCharacteristic_X.writeValue(accelerometer_X);
   accelerometerCharacteristic_Y.writeValue(accelerometer_Y);
   accelerometerCharacteristic_Z.writeValue(accelerometer_Z);
   gyroscopeCharacteristic_X.writeValue(gyroscope_X);
   gyroscopeCharacteristic_Y.writeValue(gyroscope_Y);
   gyroscopeCharacteristic_Z.writeValue(gyroscope_Z);
   temperatureCharacteristic.writeValue(temperature);
   */

    // IMU데이터 저장을 위한 버퍼
    float buffer[EI_CLASSIFIER_DSP_INPUT_FRAME_SIZE] = { 0 };
 
    for (size_t i = 0; i < EI_CLASSIFIER_DSP_INPUT_FRAME_SIZE; i += 3) {
        // 다음 틱을 감지
        uint64_t next_tick = micros() + (EI_CLASSIFIER_INTERVAL_MS * 1000);
 
        buffer[i] = myIMU.readFloatAccelX();
        buffer[i+1] = myIMU.readFloatAccelY();
        buffer[i+2] = myIMU.readFloatAccelZ();
        buffer[i+3] = myIMU.readFloatGyroX();
        buffer[i+4] = myIMU.readFloatGyroY();
        buffer[i+5] = myIMU.readFloatGyroZ();

        buffer[i + 0] *= CONVERT_TO_MS2;
        buffer[i + 1] *= CONVERT_TO_MS2;
        buffer[i + 2] *= CONVERT_TO_MS2;
        buffer[i + 3] *= CONVERT_TO_MS2;
        buffer[i + 4] *= CONVERT_TO_MS2;
        buffer[i + 5] *= CONVERT_TO_MS2;
        
        delayMicroseconds(next_tick - micros());
    }


    // 행위 분류를 위해 raw buffer를 signal로 변환
    signal_t signal;
    int err = numpy::signal_from_buffer(buffer, EI_CLASSIFIER_DSP_INPUT_FRAME_SIZE, &signal);
    if (err != 0) {
        ei_printf("Failed to create signal from buffer (%d)\n", err);
        return;
    }
 
    // MotionDetect 시작
    ei_impulse_result_t result = { 0 };
 
    err = run_classifier(&signal, &result, debug_nn);
    if (err != EI_IMPULSE_OK) {
        ei_printf("ERR: Failed to run classifier (%d)\n", err);
        return;
    }
    
    //결과출력    
    ei_printf("  %s: %.5f\n", result.classification[0].label, result.classification[0].value);
    ei_printf("  %s: %.5f\n", result.classification[1].label, result.classification[1].value);


}
