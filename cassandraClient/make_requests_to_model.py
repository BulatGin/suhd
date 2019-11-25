import random
import time
import datetime
import uuid

from cassandra.cluster import Cluster
from threading import Timer
import sys

# from cassandra.query import BatchStatement

coordinators = {
    1: ['172.31.44.69', '172.31.34.223'],
    2: ['172.31.34.223', '172.31.41.241'],
    3: ['172.31.41.241', '172.31.44.69'],
    4: ['172.31.44.69', '172.31.41.241']
}

node_number = int(sys.argv[1])

cluster = Cluster(coordinators[node_number])
session = cluster.connect()

ids_pool = range(2500*(node_number - 1) + 1, 2500*node_number + 1)  # 1..2500 || 2501..5000 || 5001..7500 || 7501..10000


def insert_records():
    t = Timer(10, insert_records)
    t.setDaemon(True)
    t.start()
    insert = session.prepare('''INSERT INTO traffic_lights.record (RID, cid, create_time, pedestrian_count, vehicle_count)
    VALUES(?, ?, ?, ?, ?)''')
    # batch = BatchStatement()
    send_time = datetime.datetime.now()
    start = time.time()
    for id in ids_pool:
        try:
            # batch.add(insert, (uuid.uuid4(), id, send_time, random.randint(0, 100), random.randint(0, 200)))
            session.execute(insert, (uuid.uuid4(), id, send_time, random.randint(0, 100), random.randint(0, 200)))
        except Exception as e:
            print('The Cassandra error: ', e)
    # session.execute(batch)
    time_diff = time.time() - start
    print('2500 records wrote in {} s'.format(time_diff))


if __name__ == '__main__':
    insert_records()
    while True:
        time.sleep(10)