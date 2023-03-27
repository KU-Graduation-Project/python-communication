###BLE로 받은 센서데이터를 Edge-Impulse에 upload할 수 있는 json 파일로 만들어준다

import asyncio
import hashlib
import hmac
import json
import random
import string
import time

from bleak import BleakClient

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
            print("Data collect start")

            while True:
                time.sleep(0.02)
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
                        gyroList[0] = data/100
                    elif characteristic.uuid == '0000ffb2-0000-1000-8000-00805f9b34fb':
                        gyroList[1] = data/100
                    elif characteristic.uuid == '0000ffb3-0000-1000-8000-00805f9b34fb':
                        gyroList[2] = data/100

                list.append(accList + gyroList)
                count+=1

                if count > 9:
                    print(list)
                    HMAC_KEY = "fed53116f20684c067774ebf9e7bcbdc"

                    # empty signature (all zeros). HS256 gives 32 byte signature, and we encode in hex, so we need 64 characters here
                    emptySignature = ''.join(['0'] * 64)

                    data = {
                        "protected": {
                            "ver": "v1",
                            "alg": "HS256",
                            "iat": time.time()  # epoch time, seconds since 1970
                        },
                        "signature": emptySignature,
                        "payload": {
                            "device_name": "91:9B:0E:7D:3E:4C:25:E",
                            "device_type": "Xiao nRF52840",
                            "interval_ms": 200,
                            "sensors": [
                                {"name": "Ax", "units": "N/A"},
                                {"name": "Ay", "units": "N/A"},
                                {"name": "Az", "units": "N/A"},
                                {"name": "Gx", "units": "N/A"},
                                {"name": "Gy", "units": "N/A"},
                                {"name": "Gz", "units": "N/A"}
                            ],
                            "values": list
                        }
                    }

                    encoded = json.dumps(data)

                    # sign message
                    signature = hmac.new(bytes(HMAC_KEY, 'utf-8'), msg=encoded.encode('utf-8'),
                                         digestmod=hashlib.sha256).hexdigest()

                    # set the signature again in the message, and encode again
                    data['signature'] = signature
                    encoded = json.dumps(data)


                    # Writing to json
                    _LENGTH = 5
                    string_pool = string.ascii_lowercase
                    random_string = ""  # 결과 값
                    for i in range(_LENGTH):
                        random_string += random.choice(string_pool)
                    file_path = "./data/"+"idle."+random_string+".json"
                    with open(file_path, "w") as outfile:
                        outfile.write(encoded)

                    break





print('disconnect')


loop = asyncio.get_event_loop()
loop.run_until_complete(run(address))
print('done')