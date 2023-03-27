import asyncio
import time
from datetime import datetime

from bleak import BleakClient

# scan시 arduino라는 이름으로 인식될 수 있음
address = "A69B7523-4CFB-77FA-3EED-B8626B9955C6"

# 0000(****)-0000 부분의 UUID만 설정하면 됨(16bit->128bit 변환)
accelerometerCharacteristic_X_uuid = "0000FFA1-0000-1000-8000-00805F9B34FB"


async def run(address):
    async with BleakClient(address) as client:
        print('connected')
        services = await client.get_services()

        accList = [0, 0, 0]
        gyroList = [0, 0, 0]
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

                    # print('\t', characteristic)
                    # print('\t\tdescription :', characteristic.description)
                    # ['write-without-response', 'write', 'read', 'notify']
                    # print('\t\tproperties :', characteristic.properties)
                print('acc | gyro:', end='')
                for data in accList:
                    print(data, ', ', end='')

                for data in gyroList:
                    print(data, ', ', end='')
                print()

    print('disconnect')


loop = asyncio.get_event_loop()
loop.run_until_complete(run(address))
print('done')
