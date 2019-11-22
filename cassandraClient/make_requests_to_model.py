import random
import time
import datetime

from cassandra.cluster import Cluster
from threading import Timer
import sys

from cassandra.query import BatchStatement

cluster = Cluster(['172.31.44.69', '172.31.34.223'])
session = cluster.connect()

node_number = int(sys.argv[1])
ids_pool = range(2500*(node_number - 1) + 1, 2500*node_number + 1)  # 1..2500 || 2501..5000 || 5001..7500 || 7501..10000


def insert_records():
    t = Timer(10, insert_records)
    t.setDaemon(True)
    t.start()
    insert = session.prepare('''INSERT INTO traffic_lights.record (cid, create_time, pedestrian_count, vehicle_count)
    VALUES(?, ?, ?, ?)''')
    batch = BatchStatement()
    send_time = datetime.datetime.now().isoformat()
    start = time.time()
    for id in ids_pool:
        try:
            batch.add(insert, (id, send_time, random.randint(0, 100), random.randint(0, 200)))
        except Exception as e:
            print('The Cassandra error: ', e)
    session.execute(batch)
    time_diff = time.time() - start
    print('2500 records wrote in {} s'.format(time_diff))


if __name__ == '__main__':
    insert_records()
    while True:
        time.sleep(10)