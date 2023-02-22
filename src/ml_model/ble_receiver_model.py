import asyncio
import time
from datetime import datetime
from bleak import BleakClient

import numpy as np
import tensorflow as tf
from tensorflow import keras

# AI 모델 불러오기
model = tf.keras.models.load_model("./lstm_model.h5", compile=False)

# scan시 arduino라는 이름으로 인식될 수 있음
address = "E69FDBAC-4750-BF6F-0C68-5646E82D36E3"

# 0000(****)-0000 부분의 UUID만 설정하면 됨(16bit->128bit 변환)
accelerometerCharacteristic_X_uuid = "0000FFA1-0000-1000-8000-00805F9B34FB"


async def run(address):
    async with BleakClient(address) as client:
        print('connected')
        services = await client.get_services()

        accList = [0, 0, 0]
        gyroList = [0, 0, 0]
        list = []

        # 데이터 결과분석 주기
        count = 0

        for service in services:
            print("service:", service)
            # print('\tuuid:', service.uuid)
            # print('\tcharacteristic list:')

            while True:
                time.sleep(0.02)
                now = datetime.now()
                timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
                print(' ', timestamp, ' ', end='')
                for characteristic in service.characteristics:
                    data = int.from_bytes(await client.read_gatt_char(characteristic.uuid), byteorder='little',
                                          signed=True)
                    if characteristic.uuid == '0000ffa1-0000-1000-8000-00805f9b34fb':
                        # characteristic uuid로 데이터 읽기(characteristic 속성에 read가 존재해야 가능)
                        accList[0] = data
                    elif characteristic.uuid == '0000ffa2-0000-1000-8000-00805f9b34fb':
                        accList[1] = data
                    elif characteristic.uuid == '0000ffa3-0000-1000-8000-00805f9b34fb':
                        accList[2] = data
                    elif characteristic.uuid == '0000ffb1-0000-1000-8000-00805f9b34fb':
                        gyroList[0] = data
                    elif characteristic.uuid == '0000ffb2-0000-1000-8000-00805f9b34fb':
                        gyroList[1] = data
                    elif characteristic.uuid == '0000ffb3-0000-1000-8000-00805f9b34fb':
                        gyroList[2] = data

                print('acc , gyro | ', end='')
                for data in accList:
                    print(data, ' ', end='')

                for data in gyroList:
                    print(data, ' ', end='')
                print()

                list.append(accList+gyroList)
                count += 1


                if count > 7:
                    test_data = np.array(list)
                    test_data = np.reshape(test_data, (len(test_data), 1, 6))

                    label = np.array(['fallforward', 'idle', 'walk'], dtype=object)
                    np_class = np.argmax(model.predict(test_data), axis=1)
                    print('----------  ', label[np_class[0]], ' ----------')

                    list = []
                    count = 0

print('disconnect')


loop = asyncio.get_event_loop()
loop.run_until_complete(run(address))
print('done')
