import datetime
import sys
import time
import uuid

import psycopg2
from cassandra.cluster import Cluster
from cassandra.query import BatchStatement
from psycopg2.extras import DictCursor

run_start_time = time.time()
camera_to_tl_dict = dict()

with psycopg2.connect("user='postgres' password='postgres' host='database-1.crzusti7h5eb.us-east-1.rds.amazonaws.com' dbname='traffic_lights'") as conn:
    with conn.cursor(cursor_factory=DictCursor) as cursor:
        cursor.execute('''SELECT TL.*, C.CID
                    FROM traffic_light TL
                    JOIN camera C ON TL.TLID = C.TLID
                    ''')
        for row in cursor:
            camera_to_tl_dict[row['cid']] = row

cluster = Cluster(['172.31.44.69', '172.31.34.223'])
session = cluster.connect()

PERIOD_TYPES = {'MIN': 60, '5MIN': 300, 'HOUR': 60*60}
period_type = sys.argv[1]
period = PERIOD_TYPES[period_type]

start_time = datetime.datetime.strptime(sys.argv[2], '%Y-%m-%dT%H:%M') if len(sys.argv) > 2 else (datetime.datetime.now() - datetime.timedelta(seconds=period))
time_delta = datetime.timedelta(seconds=period)
end_time = start_time + time_delta

rows = session.execute(f'''SELECT create_time, vehicle_count, pedestrian_count, CID 
                            FROM traffic_lights.record
                            WHERE create_time >= '{start_time.isoformat()}' 
                            AND   create_time < '{end_time.isoformat()}' ''')

VEHICLE_COUNT_CHANGES = 'vehicle_count_changes'
PEDESTRIAN_COUNT_CHANGES = 'pedestrian_count_changes'
aggregated_records_per_camera = dict()
for row in rows:
    cid = row.cid
    if cid not in aggregated_records_per_camera:
        aggregated_records_per_camera[cid] = {VEHICLE_COUNT_CHANGES: [],
                                              PEDESTRIAN_COUNT_CHANGES: []}
    else:
        camera_record = aggregated_records_per_camera[cid]
        camera_record[VEHICLE_COUNT_CHANGES].append(row.vehicle_count)
        camera_record[PEDESTRIAN_COUNT_CHANGES].append(row.pedestrian_count)

insert = session.prepare('''INSERT INTO traffic_lights.aggregated_record
     (arid, period_start, period_end, period, cid, tlid, location, pedestrian_count_changes, total_pedestrian_count, vehicle_count_changes, total_vehicle_count)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''')
batch = BatchStatement()
for cid, value in aggregated_records_per_camera.items():
    tl = camera_to_tl_dict[cid]
    batch.add(insert, (str(uuid.uuid4()), start_time.isoformat(), end_time.isoformat(),
                       period, cid, tl['tlid'], tl['location'],
                       value[PEDESTRIAN_COUNT_CHANGES], sum(value[PEDESTRIAN_COUNT_CHANGES]), value[VEHICLE_COUNT_CHANGES], sum(value[VEHICLE_COUNT_CHANGES])))
session.execute(batch)
run_end_time = time.time() - run_start_time
print(run_start_time)
