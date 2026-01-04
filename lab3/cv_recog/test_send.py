import json
import time
from confluent_kafka import Producer, Consumer
import cv2
import numpy as np
import base64

SERVER_IP='10.254.252.104:9092'
# конфигурация Producer'а
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
consumer.subscribe(["clownImageOutput","faceDbControlOutput"])




imgPath="face_base/danya/d2.jpg"
# Load JPG image to ndarray
img_ndarray = cv2.imread(imgPath)

# Encode ndarray back to JPG as bytes object
_, img_encoded = cv2.imencode('.jpg', img_ndarray)
img_bytes = img_encoded.tobytes()



msg={"useWhitelist":True,# true by default, may be implicit   if specified as false , every face on the image will be clowned
     "uid":{"SEQ":32,"NUM":1},# could be anything, just will be forwarded on response
     "imgData":base64.b64encode(img_bytes).decode('utf-8'), # img to clown 
     }
msg_json=json.dumps(msg)

producer.produce("clownImageInput", value=msg_json)
producer.flush()
