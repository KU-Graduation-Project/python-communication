import json
import multiprocessing
from datetime import datetime
import asyncio
from bleak import BleakClient

import paho.mqtt.client as mqtt
from random import randint
import time

# scan시 arduino라는 이름으로 인식될 수 있음
address = "E69FDBAC-4750-BF6F-0C68-5646E82D36E3"
# 0000(****)-0000 부분의 UUID만 설정하면 됨(16bit->128bit 변환)
accelerometerCharacteristic_X_uuid = "0000FFA1-0000-1000-8000-00805F9B34FB"

accList = [0, 0, 0]
gyroList = [0, 0, 0]
list = []

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        global Connected
        Connected = True
    else:
        print("Connection failed")


def client_connect(user):
    # MQTT connection
    cli = "producer" + user
    mqtt_client = mqtt.Client(cli)
    mqtt_client.on_connect = on_connect

    mqtt_broker_address = '127.0.0.1'
    mqtt_client.connect(mqtt_broker_address, 1883)
    mqtt_client.loop_start()
    #while Connected != True:
    #    time.sleep(0.1)
    return mqtt_client


async def run(address):
    async with BleakClient(address) as client:
        services = await client.get_services()

        for service in services:

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


def make_producer(user) :
    mqtt_client = client_connect(user)
    while True:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(run(address))
        randNumber = randint(0, 360)
        now = datetime.now()
        timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
        # json으로 encode해서 publish
        if mqtt_client.publish(user, json.dumps({"user": user, "timestamp": str(timestamp), "data": randNumber}), 1):
            print(user+'_MQTT published : ' + json.dumps({"user": user, "timestamp": str(timestamp), "data": accList[0]}))

        time.sleep(2)


user_list = ["user1", "user2", "user3", "user4", "user5", "user6", "user7", "user8", "user9", "user10"]


if __name__=='__main__':
    # 컨슈머 멀티프로세싱
    pool = multiprocessing.Pool(processes=10)
    pool.map(make_producer, user_list)
