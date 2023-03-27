import json
import multiprocessing
from asyncio.log import logger

import pymysql
from kafka import KafkaConsumer

"""user# 토픽에서 데이터 받아 db에 저장"""



class MessageConsumer:
    topic =""

    def __init__(self, topic):
        self.topic = topic
        # DB연결
        self.conn = pymysql.connect(host='127.0.0.1', user='root', password='password', db='motionDB', charset='utf8')
        self.cur = self.conn.cursor()
        sql = 'DROP TABLE IF EXISTS ' + self.topic
        self.cur.execute(sql)

        print(self.topic + " table created")
        sql = 'CREATE TABLE ' + self.topic + ' (timestamp datetime PRIMARY KEY, ' \
                                             'a_x int(3), a_y int(3), a_z int(3),' \
                                             'g_x int(3), g_y int(3), g_z int(3), ' \
                                             'heartrate int(3), resp int(3), temp int(3))'
        self.cur.execute(sql)
        self.conn.commit()

        self.activate_listener()


    def activate_listener(self):
        consumer = KafkaConsumer(bootstrap_servers='localhost:9092',
                                 group_id='team',
                                 consumer_timeout_ms=60000,
                                 auto_offset_reset='earliest',
                                 enable_auto_commit=False,
                                 #value_deserializer=lambda m: json.loads(m.decode('utf-8'))
                                 )

        consumer.subscribe(self.topic)
        print(self.topic + ": consumer open")
        try:
            for message in consumer:
                m_decode = str(message.value.decode("utf-8", "ignore"))
                m_in = m_decode[:len(m_decode)]


                m_json = json.loads(m_in)
                timestamp = m_json["timestamp"]
                g_x = str(m_json["data"])
                sql = 'INSERT INTO ' + self.topic + ' (timestamp, g_x) VALUES (\''+timestamp+'\', '+g_x+');'
                if self.cur.execute(sql):
                    print(self.topic + " DB save : " + str(m_json))
                # committing message manually after reading from the topic
                self.conn.commit()
                consumer.commit()

        except Exception as e:
            print(e)
            logger.exception("failed to create %s", e)

        finally:
            consumer.close()


if __name__ == '__main__':
    user_list = ["user1", "user2", "user3", "user4", "user5", "user6", "user7", "user8", "user9", "user10"]

    pool = multiprocessing.Pool(processes=10)
    pool.map(MessageConsumer, user_list)

