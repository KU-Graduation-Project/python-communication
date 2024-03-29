import asyncio
import time
from datetime import datetime
from bleak import BleakClient

import numpy as np
import tensorflow as tf
from tensorflow import keras

# AI 모델 불러오기
model = tf.keras.models.load_model("./lstm_model.h5", compile=False)

# scan시 Arduino라는 이름으로 인식될 수 있음
# 배터리 없는 모델
#address = "E69FDBAC-4750-BF6F-0C68-5646E82D36E3"
#배터리 있는 모델
address = "A69B7523-4CFB-77FA-3EED-B8626B9955C6"

# 0000(****)-0000 부분의 UUID만 설정하면 됨(16bit->128bit 변환)
accelerometerCharacteristic_X_uuid = "0000FFA1-0000-1000-8000-00805F9B34FB"


#BLE notify로 보낸 데이터를 받는 콜백함수
def notify_callback(sender: int, data: bytearray):
    data = int.from_bytes(data)
    return data
    print('sender: ', sender, 'data: ', data)


async def run(address):
    async with BleakClient(address) as client:
        services = await client.get_services()


        dataList = [0, 0, 0, 0, 0, 0]
        list = []

        # 데이터 결과분석 주기
        count = 0

        for service in services:
            print("service:", service)
            # print('\tuuid:', service.uuid)
            # print('\tcharacteristic list:')

            while True:
                #time.sleep(0.01)
                now = datetime.now()
                timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
                print(' ', timestamp, ' ', end='')
                for characteristic in service.characteristics:
                    await client.start_notify(characteristic, notify_callback)
                    data = int.from_bytes(await client.read_gatt_char(characteristic.uuid),
                         byteorder='little', signed=True)
                    #data = int.from_bytes(await client.start_notify(characteristic, notify_callback),
                         #byteorder='little', signed=True)

                    if characteristic.uuid == '0000ffa1-0000-1000-8000-00805f9b34fb':
                        # characteristic uuid로 데이터 읽기(characteristic 속성에 read가 존재해야 가능)
                        dataList[0] = data
                    elif characteristic.uuid == '0000ffa2-0000-1000-8000-00805f9b34fb':
                        dataList[1] = data
                    elif characteristic.uuid == '0000ffa3-0000-1000-8000-00805f9b34fb':
                        dataList[2] = data
                    elif characteristic.uuid == '0000ffb1-0000-1000-8000-00805f9b34fb':
                        dataList[3] = data
                    elif characteristic.uuid == '0000ffb2-0000-1000-8000-00805f9b34fb':
                        dataList[4] = data
                    elif characteristic.uuid == '0000ffb3-0000-1000-8000-00805f9b34fb':
                        dataList[5] = data


                print('acc , gyro | ', end='')
                for data in dataList:
                    print(data, ' ', end=' ')

                print()

                list.append(dataList)
                count += 1


                if count > 7:
                    test_data = np.array(list)
                    test_data = np.reshape(test_data, (len(test_data), 1, 6))

                    label = np.array(['fallforward', 'idle', 'walk'], dtype=object)
                    np_class = np.argmax(model.predict(test_data), axis=1)
                    print('----------  ', label[np_class[0]], ' ----------')

                    list = []
                    count = 0

loop = asyncio.get_event_loop()
loop.run_until_complete(run(address))
print('done')
print('disconnect')
