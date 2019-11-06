import random
import uuid

from cassandra.cluster import Cluster

cluster = Cluster(['172.31.44.69', '172.31.34.223'])
session = cluster.connect()

session.execute('''
    CREATE KEYSPACE IF NOT EXISTS traffic_lights
    WITH REPLICATION = {'class': 'SimpleStrategy', 'replication_factor': 3}
''')
session.execute('''
    CREATE TABLE IF NOT EXISTS traffic_lights.record (
        RID UUID,
        create_time timestamp,
        vehicle_count smallint,
        pedestrian_count smallint,
        CID int,
        PRIMARY KEY ((RID), CID, create_time)
)''')

for i in range(5000):
    session.execute(f'''
        INSERT INTO traffic_lights.record
        (RID, create_time, vehicle_count, pedestrian_count, CID)
        VALUES (
            {str(uuid.uuid4())},
            toTimestamp(now()),
            {random.randint(0, 100)},
            {random.randint(0, 200)},
            {random.randint(0, 10_000)}
        )
    ''')
