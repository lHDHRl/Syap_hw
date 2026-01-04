import json
import random
import time
from confluent_kafka import Producer, Consumer
from clowner import Clowner
from face_recognitio import FaceRecognizer


#connect to server
SERVER_IP='10.254.252.104:9092'
FACE_DB_PATH="./face_base/"

producerConfig = {
    'bootstrap.servers':SERVER_IP ,
    'client.id': 'clown-transformer-producer'
}
consumerConfig = {
    'bootstrap.servers':SERVER_IP ,
    'group.id': 'clown-transformer',              
    'auto.offset.reset': 'earliest'   
}

producer = Producer(producerConfig)
consumer = Consumer(consumerConfig)

consumer.subscribe(["clownImageInput","faceDbControlInput"])


#prepeare base and clowner

clowner= Clowner()
faces_db=FaceRecognizer(FACE_DB_PATH)

#load index
faces_db.build_database()



def processFaceTask():
    gloval 

while True:
    msg = consumer.poll(1.0)
    if msg is None:
        continue
    if msg.error():
        print(f"Consumer error: {msg.error()}")
        continue
    print(f"Received message from topic {msg.topic()}: {msg.value().decode('utf-8')}")