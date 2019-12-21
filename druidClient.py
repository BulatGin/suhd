import datetime
import json
import random
import uuid

# from kafka import KafkaProducer

TOPIC = 'tf'

# producer = KafkaProducer(bootstrap_servers='34.238.162.107:9092')

with open('data.json', 'w', encoding='utf-8') as out_file:
    send_time = datetime.datetime.now()
    for _ in range(60):
        for i in range(5000):
            send_time = send_time + datetime.timedelta(milliseconds=5)
            data = {
                'RID': str(uuid.uuid4()),
                'cid': i,
                'create_time': send_time.isoformat(),
                'pedestrian_count': random.randint(0, 100),
                'vehicle_count': random.randint(0, 200)
            }
            data_str = json.dumps(data)
            out_file.write(data_str + '\n')
        send_time = send_time + datetime.timedelta(minutes=1)
