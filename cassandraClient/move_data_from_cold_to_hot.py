import datetime
import sys
import time
import uuid

import psycopg2
from cassandra.cluster import Cluster
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

relational_db_read_time = time.time() - run_start_time

cluster = Cluster(['172.31.44.69', '172.31.34.223'])
session = cluster.connect()

PERIOD_TYPES = {'MIN': 60, '5MIN': 300, 'HOUR': 60*60}
period_type = sys.argv[1]
period = PERIOD_TYPES[period_type]

start_time = datetime.datetime.strptime(sys.argv[2], '%Y-%m-%dT%H:%M:%S') if len(sys.argv) > 2 else (datetime.datetime.now() - datetime.timedelta(seconds=period))
time_delta = datetime.timedelta(seconds=period)
end_time = start_time + time_delta

cameras_in_chunk = 250

chunks_read_times = []
chunks_process_times = []
chunks_write_times = []

for i in range(len(camera_to_tl_dict) // cameras_in_chunk):
    chunk_read_time_start = time.time()
    rows = session.execute(session.prepare(f'''SELECT create_time, vehicle_count, pedestrian_count, CID
                                FROM traffic_lights.record
                                WHERE cid in {tuple(range(cameras_in_chunk * i + 1, cameras_in_chunk * (i + 1) + 1))}
                                AND create_time >= ?
                                AND   create_time < ?
                                ALLOW FILTERING'''), (start_time, end_time))

    chunk_read_time = time.time() - chunk_read_time_start
    chunk_process_time_start = time.time()
    VEHICLE_COUNT_CHANGES = 'vehicle_count_changes'
    PEDESTRIAN_COUNT_CHANGES = 'pedestrian_count_changes'
    aggregated_records_dicts_per_camera = dict()
    for row in rows:
        cid = row.cid
        if cid not in aggregated_records_dicts_per_camera:
            aggregated_records_dicts_per_camera[cid] = {VEHICLE_COUNT_CHANGES: dict(),
                                                        PEDESTRIAN_COUNT_CHANGES: dict()}
        camera_record = aggregated_records_dicts_per_camera[cid]
        create_time = row.create_time.timestamp()
        camera_record[VEHICLE_COUNT_CHANGES][create_time] = row.vehicle_count
        camera_record[PEDESTRIAN_COUNT_CHANGES][create_time] = row.pedestrian_count

    aggregated_records_per_camera = dict()
    for cid, record_set in aggregated_records_dicts_per_camera.items():
        aggregated_records_per_camera[cid] = dict()
        aggregated_records_per_camera[cid][VEHICLE_COUNT_CHANGES] = list(map(lambda pair: pair[1], sorted(record_set[VEHICLE_COUNT_CHANGES].items(), key=lambda item: item[0])))
        aggregated_records_per_camera[cid][PEDESTRIAN_COUNT_CHANGES] = list(map(lambda pair: pair[1], sorted(record_set[PEDESTRIAN_COUNT_CHANGES].items(), key=lambda item: item[0])))

    chunk_process_time = time.time() - chunk_process_time_start

    chunk_write_time_start = time.time()
    insert = session.prepare('''INSERT INTO traffic_lights.aggregated_record
         (arid, period_start, period_end, period, cid, tlid, location, pedestrian_count_changes, total_pedestrian_count, vehicle_count_changes, total_vehicle_count)
          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''')
    for cid, value in aggregated_records_per_camera.items():
        tl = camera_to_tl_dict[cid]
        session.execute(insert, (uuid.uuid4(), start_time, end_time,
                           period, cid, tl['tlid'], tuple(map(float,tl['location'].strip('()').split(','))),
                           value[PEDESTRIAN_COUNT_CHANGES], sum(value[PEDESTRIAN_COUNT_CHANGES]), value[VEHICLE_COUNT_CHANGES], sum(value[VEHICLE_COUNT_CHANGES])))

    chunk_write_time = time.time() - chunk_write_time_start

    chunks_read_times.append(chunk_read_time)
    chunks_process_times.append(chunk_process_time)
    chunks_write_times.append(chunk_write_time)
run_end_time = time.time() - run_start_time

total_read_time = sum(chunks_read_times)
chunk_avg_read_time = total_read_time / len(chunks_read_times)
total_process_time = sum(chunks_process_times)
chunk_avg_process_time = total_process_time / len(chunks_process_times)
total_write_time = sum(chunks_write_times)
chunk_avg_write_time = total_write_time / len(chunks_write_times)
print(f'''
    TOTAL TIME = {run_end_time}
    LOAD_REFERENCES_FROM_RELATIONAL_DB = {relational_db_read_time}
    READ_TIME = {total_read_time}; average_per_chunk = {chunk_avg_read_time}
    PROCESS_TIME = {total_process_time}; average_per_chunk = {chunk_avg_process_time}
    WRITE_TIME = {total_write_time}; average_per_chunk = {chunk_avg_write_time}
''')

