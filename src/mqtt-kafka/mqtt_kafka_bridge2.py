import json
import threading

from pykafka import KafkaClient
import paho.mqtt.client as mqtt
import time

mqtt_broker_address = '127.0.0.1'
mqtt_client = mqtt.Client('MQTTConsumer')
mqtt_client.connect(mqtt_broker_address)

kafka_client = KafkaClient(hosts='localhost:9092')


def on_message(client, userdata, message):
    m_decode = str(message.payload.decode("utf-8", "ignore"))
    m_in = json.loads(m_decode)
    topic = m_in["user"]

    kafka_topic = kafka_client.topics[topic]  # 토픽 지정
    kafka_producer = kafka_topic.get_sync_producer()

    msg_payload = str(message.payload)
    print('Received MQTT message ', msg_payload)
    kafka_producer.produce(str(msg_payload).encode('ascii'))
    print('KAFKA : Just published ' + str(msg_payload) + 'to' + topic)


def on_client(topic):
    mqtt_client.loop_start()
    mqtt_client.subscribe(topic)  # 토픽 지정
    mqtt_client.on_message = on_message
    time.sleep(400)
    mqtt_client.loop_stop()


t2 = threading.Thread(target=on_client("test2"))
t3 = threading.Thread(target=on_client("test3"))
t4 = threading.Thread(target=on_client("test4"))
t5 = threading.Thread(target=on_client("test5"))

t2.start()
t3.start()
t4.start()
t5.start()
